"""Resume missed boundaries/extra official candidates after initial queue."""
import json,time,logging
from backend.config import ROOT,DATA,write_json
from backend.readiness import check
from pipeline.sentinel2_chlorophyll import process
from scripts.prepare_scale_candidates import CANDIDATES
logging.basicConfig(level=logging.INFO)
p=ROOT/'output/scale-processing-results.json'
while len(json.loads(p.read_text()))<34 or not (DATA/'internal/scale-discovery-complete.json').exists():time.sleep(3)
results=json.loads(p.read_text())
for rid,name,_,_ in CANDIDATES:
 pending=json.loads((DATA/'internal/pending-reservoirs.json').read_text());public=json.loads((DATA/'reservoirs.json').read_text());original=set(json.loads((DATA/'internal/original-sixteen-scale-snapshot.json').read_text()))
 complete=[r for r in pending+public if r['id'] not in original and r.get('identity_verification',{}).get('identity_verified') and check(r)['ready']]
 # Basava/Malaprabha identity is supplied by the prior government's audit.
 for extra in ['basava-sagara','malaprabha']:
  record=next((r for r in pending if r['id']==extra),None)
  if record and check(record)['ready'] and record not in complete:complete.append(record)
 if len(complete)>=30:break
 r=next((r for r in pending if r['id']==rid),None)
 if not r or not r.get('identity_verification',{}).get('identity_verified'):continue
 if check(r)['ready']:continue
 prior=next((x for x in reversed(results) if x['id']==rid),{})
 # Reattempt previously missing boundaries and transport failures; preserve genuine QC failures.
 if prior.get('attempts') and not any('HTTP' in a.get('reason','') or 'RasterioIOError' in a.get('reason','') for a in prior['attempts']):continue
 try:process(rid,2);entry={'id':rid,'readiness':check(r),'resumed':True}
 except Exception as exc:entry={'id':rid,'reason':str(exc),'attempts':getattr(exc,'attempts',[]),'resumed':True}
 results=[x for x in results if x['id']!=rid]+[entry];write_json(p,results);print('RESUMED_RESULT',entry,flush=True)
write_json(DATA/'internal/scale-processing-complete.json',{'complete':True})
