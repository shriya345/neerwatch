import json,time,logging
from backend.config import ROOT,DATA,write_json
from pipeline.sentinel2_chlorophyll import process
from backend.readiness import check
logging.basicConfig(level=logging.INFO)
p=ROOT/'output/coverage-batch-results.json'
while len(json.loads(p.read_text()))<8:time.sleep(2)
results=json.loads(p.read_text())
for rid in ['nugu','kadra']:
 try:
  result=process(rid,2);record=next(r for r in json.loads((DATA/'internal/pending-reservoirs.json').read_text()) if r['id']==rid)
  entry={'id':rid,'readiness':check(record),'scene_id':result['item_id'],'chlorophyll_a':result['chlorophyll_a']}
 except Exception as exc:entry={'id':rid,'error':str(exc),'attempts':getattr(exc,'attempts',[])}
 results.append(entry);write_json(p,results);print('BATCH_RESULT '+json.dumps(entry),flush=True)
