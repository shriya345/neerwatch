"""Publish FAI only from frozen operational NPZs; never touches fai-history job files."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.ndimage import binary_erosion,binary_dilation
from backend.config import ROOT,DATA
VERSION='fai-scl-60m-v1'
def build():
 registry=(DATA/'reservoirs.json').read_bytes();records=json.loads(registry);out={}
 for r in records:
  directory=DATA/'sentinel2'/r['id'];history=directory/'history.json';before=history.read_bytes();rows=[]
  for h in json.loads(before):
   p=directory/(h['item_id']+'-bands.npz');raw=p.read_bytes();import io
   with np.load(io.BytesIO(raw)) as z:
    poly=z['polygon_mask'].astype(bool);approved='_scl' in z
    mask=binary_erosion(poly&(z['_scl']==6))&~binary_dilation(np.isin(z['_scl'],[3,8,9,10])) if approved else z['valid_mask'].copy()
    for b in ['B04','B08','B11']:mask &= np.isfinite(z[b])&(z[b]>0)&(z[b]<=1)
    n=int(mask.sum());coverage=n/max(1,int(poly.sum()))
    if n<25 or coverage<.1:continue
    fai=z['B08']-(z['B04']+(z['B11']-z['B04'])*(.842-.665)/(1.610-.665))
    rows.append(dict(observed_at=h['observed_at'],item_id=h['item_id'],fai=float(np.median(fai[mask])),units='dimensionless',qc='approved' if approved else 'legacy_mask_incomplete',method=VERSION,valid_pixels=n,valid_fraction=coverage,source='Copernicus Sentinel-2 L2A',source_url=h['source_url'],array_sha256=hashlib.sha256(raw).hexdigest()))
   if p.read_bytes()!=raw:raise RuntimeError('Source changed during snapshot validation; retry later')
  if history.read_bytes()!=before:raise RuntimeError('History changed during snapshot validation')
  out[r['id']]=sorted(rows,key=lambda x:x['observed_at'])
 payload={'version':VERSION,'registry_sha256':hashlib.sha256(registry).hexdigest(),'observations':out}
 target=DATA/'fai-snapshots'/'observed-v1.json';target.parent.mkdir(exist_ok=True);tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(payload,indent=2,allow_nan=False));tmp.replace(target)
 return target
if __name__=='__main__':print(build())
