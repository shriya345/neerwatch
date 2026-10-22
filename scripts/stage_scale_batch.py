"""Stage independently audited candidates; publish only after live API/UI audit."""
import json,hashlib,argparse
from backend.config import DATA,ROOT,write_json
from scripts.admit_coverage_candidates import verify_pair
from scripts.prepare_scale_candidates import CANDIDATES
from backend.readiness import check
parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
snapshot=json.loads((DATA/'internal/original-sixteen-scale-snapshot.json').read_text());original=set(snapshot)
for paths in snapshot.values():
 for relative,digest in paths.items():assert hashlib.sha256((DATA/relative).read_bytes()).hexdigest()==digest
public=json.loads((DATA/'reservoirs.json').read_text());pending=json.loads((DATA/'internal/pending-reservoirs.json').read_text())
known={r['id']:r for r in public+pending};identities={i['id']:i for i in json.loads((DATA/'internal/coverage-identity-audit.json').read_text())};identities.update({i['id']:i for i in json.loads((DATA/'internal/scale-discovery-audit.json').read_text()) if i.get('identity_verified')})
order=['basava-sagara','malaprabha']+[c[0] for c in CANDIDATES];staged=[r for r in public if r['id'] in original];audit=[]
if args.publish:
 staged=json.loads((DATA/'internal/scale-staged-reservoirs.json').read_text());audit=json.loads((ROOT/'output/scale-admission-audit.json').read_text());order=[]
for rid in order:
 if rid in original or rid not in known:continue
 if len(staged)>=46:break
 r=known[rid];identity=r.get('identity_verification',identities.get(rid,{}))
 if not identity.get('identity_verified'):continue
 try:
  from shapely.geometry import shape,Point
  geometry=shape(json.loads((DATA/'boundaries'/f'{rid}.geojson').read_text())['geometry'])
  if not geometry.covers(Point(r['longitude'],r['latitude'])):
   point=geometry.representative_point();r.update(latitude=point.y,longitude=point.x,coordinate_role='Interior point of the verified reservoir water polygon')
  evidence=verify_pair(r);r.pop('pending_reasons',None);r['identity_verification']=identity;staged.append(r);audit.append(evidence)
 except Exception as exc:audit.append({'id':rid,'reason':str(exc),'admitted':False})
write_json(DATA/'internal/scale-staged-reservoirs.json',staged);write_json(ROOT/'output/scale-admission-audit.json',audit)
if args.publish:
 ui=json.loads((ROOT/'output/public-frontend-state-verification.json').read_text());spectral=json.loads((ROOT/'output/processing-verification.json').read_text())
 for r in staged:
  assert len([x for x in ui if x['reservoir']==r['id'] and x['display']=='PASS'])==2,r['id']
  assert any(x['reservoir_id']==r['id'] and x.get('spectral_array_and_geotiff_verified') for x in spectral),r['id']
 ids={r['id'] for r in staged};write_json(DATA/'reservoirs.json',staged);write_json(DATA/'internal/pending-reservoirs.json',[r for r in pending if r['id'] not in ids])
print('PUBLISHED' if args.publish else 'STAGED',len(staged),'NEW',len(staged)-16)
