"""Sequential preprocessing. Admission is a separate audited step."""
import json,logging,time
from backend.config import ROOT,DATA,write_json
from pipeline.sentinel2_chlorophyll import process
from backend.readiness import check
logging.basicConfig(level=logging.INFO)
ids=['hemavathi','almatti','basava-sagara','linganamakki','malaprabha','hidkal','yagachi','markonahalli']
results=[]
for rid in ids:
 started=time.time()
 try:
  result=process(rid,2)
  r=next(r for r in json.loads((DATA/'internal/pending-reservoirs.json').read_text()) if r['id']==rid)
  status=check(r);entry={'id':rid,'readiness':status,'scene_id':result['item_id'],'chlorophyll_a':result['chlorophyll_a']}
 except Exception as exc:entry={'id':rid,'error':str(exc),'attempts':getattr(exc,'attempts',[])}
 entry['elapsed_seconds']=round(time.time()-started);results.append(entry)
 write_json(ROOT/'output/coverage-batch-results.json',results)
 print('BATCH_RESULT '+json.dumps(entry),flush=True)
