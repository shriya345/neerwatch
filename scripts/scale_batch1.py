import logging,json
from backend.config import DATA,ROOT,write_json
from pipeline.sentinel2_chlorophyll import process
logging.basicConfig(level=logging.INFO)
path=ROOT/'output/scale-processing-results.json'
results=json.loads(path.read_text()) if path.exists() else []
for rid in ['basava-sagara','malaprabha']:
 try:
  r=process(rid,2);entry={'id':rid,'result':r['chlorophyll_a'],'scene_id':r['item_id']}
 except Exception as exc:entry={'id':rid,'reason':str(exc),'attempts':getattr(exc,'attempts',[])}
 results=[x for x in results if x['id']!=rid]+[entry];write_json(ROOT/'output/scale-processing-results.json',results);print('RESULT',entry,flush=True)
