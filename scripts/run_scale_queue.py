"""Resumable sequential candidate queue; unready records remain private."""
import time,json,logging
from backend.config import DATA,ROOT,write_json
from backend.readiness import check
from pipeline.sentinel2_chlorophyll import process
from scripts.prepare_scale_candidates import CANDIDATES
logging.basicConfig(level=logging.INFO)
path=ROOT/'output/scale-processing-results.json'
while not path.exists() or len(json.loads(path.read_text()))<2:time.sleep(3)
results=json.loads(path.read_text())
for rid,name,_,_ in CANDIDATES:
 public=json.loads((DATA/'reservoirs.json').read_text())
 if len(public)>=46:break
 if any(r['id']==rid for r in public):continue
 while True:
  auditpath=DATA/'internal/scale-discovery-audit.json';audit=json.loads(auditpath.read_text()) if auditpath.exists() else []
  candidate=next((a for a in audit if a['id']==rid),None)
  if candidate and (candidate.get('identity_verified') or (DATA/'internal/scale-discovery-complete.json').exists()):break
  time.sleep(3)
 record=next((r for r in json.loads((DATA/'internal/pending-reservoirs.json').read_text()) if r['id']==rid),None)
 if not candidate.get('identity_verified') or not record:
  entry={'id':rid,'reason':candidate.get('reason','Boundary/identity not verified')};results.append(entry);write_json(path,results);continue
 if any(r['id']==rid for r in results):continue
 try:
  if not check(record)['ready']:process(rid,2)
  state=check(record);entry={'id':rid,'readiness':state,'reason':'; '.join(state['reasons']) if not state['ready'] else None}
 except Exception as exc:entry={'id':rid,'reason':str(exc),'attempts':getattr(exc,'attempts',[])}
 results.append(entry);write_json(path,results);print('QUEUE_RESULT',entry,flush=True)
