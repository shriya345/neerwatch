"""Admit only verified identities with two independently audited spectral outputs."""
import json,hashlib
import numpy as np
import rasterio
from backend.config import DATA,ROOT,write_json
from backend.active import monitoring
from backend.readiness import check
from backend.epa import classify

def verify_pair(record):
 rid=record['id'];state=check(record)
 if not state['ready']:raise ValueError('; '.join(state['reasons']))
 m=monitoring(rid);root=DATA/'sentinel2'/rid
 for row in [m['latest'],m['previous']]:
  with np.load(root/f"{row['item_id']}-bands.npz") as a:
   mask=a['valid_mask'];red=a['B04'].astype('float64');edge=a['B05'].astype('float64')
   with np.errstate(invalid='ignore',divide='ignore'):expected=(35.75*edge/red-19.3)**1.124
   assert np.allclose(expected[mask],a['chlorophyll_a'][mask],rtol=2e-5)
   assert np.isclose(np.median(expected[mask]),row['chlorophyll_a'],rtol=2e-5)
   assert int(mask.sum())==row['quality']['algorithm_valid_pixels']
   assert (a['polygon_mask'] & (a['_scl']==6)).sum()>25
   assert np.all(mask<=a['polygon_mask'])
   with rasterio.open(root/row['chlorophyll_raster_file']) as src:
    assert src.tags()['scene_id']==row['item_id'] and src.crs.to_epsg()==32643
    assert np.allclose(src.read(1)[mask],expected[mask],rtol=2e-5)
  assert row['reservoir_id']==rid and classify(row['chlorophyll_a'])
 return {'id':rid,'earlier_date':m['previous']['observed_at'],'latest_date':m['latest']['observed_at'],'latest_concentration':m['chlorophyll_a'],'earlier_concentration':m['previous']['chlorophyll_a'],'change_percent':m['change']['percent'],'category':m['classification']['name'],'latest_scene':m['latest']['item_id'],'earlier_scene':m['previous']['item_id'],'boundary':'PASS','spectral_pair_audit':'PASS'}

if __name__=='__main__':
 identities=json.loads((DATA/'internal/coverage-identity-audit.json').read_text());ids={i['id']:i for i in identities}
 pending=json.loads((DATA/'internal/pending-reservoirs.json').read_text());public=json.loads((DATA/'reservoirs.json').read_text());evidence=[];kept=[]
 for record in pending:
  rid=record['id']
  if rid not in ids or not ids[rid]['identity_verified']:kept.append(record);continue
  try:
   result=verify_pair(record);record.pop('pending_reasons',None);record['identity_verification']=ids[rid];public.append(record);evidence.append(result)
  except Exception as exc:record['pending_reasons']=[str(exc)];kept.append(record);evidence.append({'id':rid,'admitted':False,'reason':str(exc)})
 # Preserve original operational outputs byte-for-byte.
 for rid,files in json.loads((DATA/'internal/original-eight-coverage-snapshot.json').read_text()).items():
  for name,digest in files.items():
   path=DATA/'boundaries'/name if name.endswith('.geojson') else DATA/'sentinel2'/rid/name
   assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,(rid,name)
 write_json(DATA/'reservoirs.json',public);write_json(DATA/'internal/pending-reservoirs.json',kept);write_json(ROOT/'output/coverage-admission-audit.json',evidence)
 print(json.dumps(evidence,indent=2));print('PUBLIC',len(public),'PENDING',len(kept))
