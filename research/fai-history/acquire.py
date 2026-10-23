"""Checkpointed real Sentinel-2 FAI history, restricted to the current registry."""
import sys,json,time,hashlib,inspect,threading,concurrent.futures
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import httpx,numpy as np
from shapely.geometry import shape
import pipeline.satellite as sat
from pipeline.mosaic import observations
# Isolated reader adaptation: three FAI bands and no chlorophyll feature dependency.
src=inspect.getsource(sat.read_item).replace("result=extract_features(arrays,scl,mask,resolution)","result={'status':'available','quality':{},'features':{}}")
src=src.replace("response=client.get(f'https://planetarycomputer.microsoft.com/api/sas/v1/token/{account}/{container}')","response=client.get(f'https://planetarycomputer.microsoft.com/api/sas/v1/token/{account}/{container}',params={'refresh':int(time.time())})")
namespace=dict(sat.__dict__);namespace['BANDS']=['B04','B08','B11'];exec(src,namespace);read=namespace['read_item']
O=ROOT/'data/fai-history';O.mkdir(exist_ok=True);rs=json.loads((ROOT/'data/reservoirs.json').read_text());assert len(rs)==46
manifest={'start':'2022-01-01','end':'2026-10-22','registry_sha256':hashlib.sha256((ROOT/'data/reservoirs.json').read_bytes()).hexdigest(),'resolution_m':60,'bands':['B04','B08','B11'],'method':'FAI median B08-[B04+(B11-B04)*(842-665)/(1610-665)]','note':'October capped at present 22 October 2026; no future acquisitions'};(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
def get(url,params=None):
 for n in range(6):
  try:
   r=httpx.get(url,params=params,timeout=60)
   if r.status_code in [429,500,502,503,504]:time.sleep(min(60,float(r.headers.get('retry-after',2**n))));continue
   r.raise_for_status();return r.json()
  except Exception:
   if n==5:raise
   time.sleep(2**n)
 raise RuntimeError('Catalogue retries exhausted')
def catalogue(r):
 rid=r['id'];p=O/rid;p.mkdir(exist_ok=True);g=json.loads((ROOT/f'data/boundaries/{rid}.geojson').read_text())['geometry'];pages=p/'catalogue';pages.mkdir(exist_ok=True);items={}
 for year in range(2022,2027):
  url=sat.STAC;params={'collections':'sentinel-2-l2a','bbox':','.join(map(str,shape(g).bounds)),'datetime':f'{year}-01-01T00:00:00Z/{year}-'+('10-22' if year==2026 else '12-31')+'T23:59:59Z','limit':100,'sortby':'properties.datetime'};page=0
  while url:
   f=pages/f'{year}-{page}.json'
   if f.exists():q=json.loads(f.read_text())
   else:
    q=get(url,params);f.write_text(json.dumps(q));time.sleep(.5)
   for item in q['features']:items[item['id']]=item
   link=next((l for l in q.get('links',[]) if l.get('rel')=='next'),None);url=link['href'] if link else None;params=None;page+=1
 candidates=observations(list(items.values()),g);dedup={}
 for item in candidates:
  prop=item['properties'];key=(prop['datetime'][:10],prop.get('platform'),prop.get('sat:relative_orbit'))
  coverage=shape(item['geometry']).intersection(shape(g)).area/shape(g).area
  score=(coverage,-float(prop.get('eo:cloud_cover',100)),item['id'])
  if key not in dedup or score>dedup[key][0]:dedup[key]=(score,item)
 work=[v[1] for v in dedup.values()];(p/'catalogue-summary.json').write_text(json.dumps({'raw_scenes':len(items),'deduplicated_acquisitions':len(work),'complete':True}));print('CATALOGUE',rid,len(items),len(work),flush=True);return r,g,work

def process(job):
 r,g,item=job;rid=r['id'];p=O/rid;key=hashlib.sha256(item['id'].encode()).hexdigest()[:20];f=p/(key+'.json')
 if f.exists():
  prior=json.loads(f.read_text())
  if prior.get('status')=='valid' or prior.get('reason','').startswith(('InsufficientWaterError:','ValueError:')):return
 base={'reservoir_id':rid,'scene_id':item['id'],'acquisition':item['properties']['datetime'],'sources':[f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/{t['id']}" for t in item.get('_mosaic_items',[item])],'version':'fai-history-v1'}
 try:
  if shape(item['geometry']).intersection(shape(g)).area/shape(g).area<.95:raise ValueError('footprint_below_95_percent')
  for attempt in range(3):
   try:
    result,a,m=read(item,g);break
   except (sat.InsufficientWaterError,ValueError):raise
   except Exception:
    if attempt==2:raise
    with sat.TOKEN_LOCK:sat.TOKEN_CACHE.clear()
    time.sleep(2**attempt)
  valid=a['_valid_water_mask'];count=int(valid.sum());fraction=count/max(1,int(m.sum()))
  if count<25 or fraction<.1:raise ValueError(f'insufficient_valid_FAI_pixels:{count};coverage:{fraction}')
  fai=a['B08']-(a['B04']+(a['B11']-a['B04'])*(.842-.665)/(1.610-.665));np.savez_compressed(p/(key+'.npz'),**a,polygon_mask=m)
  base.update(status='valid',fai=float(np.median(fai[valid])),valid_pixels=count,valid_fraction=fraction,band_metadata=result['spectral_bands'],quality=result['quality'],scl_saved=True)
 except Exception as e:base.update(status='rejected_or_error',reason=f'{type(e).__name__}: {e}')
 tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(base));tmp.replace(f);print('PIXELS',rid,base['acquisition'],base['status'],flush=True)

if __name__=='__main__':
 jobs=[]
 for r in rs:
  try:
   rec,g,items=catalogue(r);jobs.extend((rec,g,i) for i in items)
  except Exception as e:print('CATALOGUE_ERROR',r['id'],str(e),flush=True)
 # Round-robin reservoir/date progress, oldest first, avoids completing only one reservoir.
 jobs.sort(key=lambda j:(j[2]['properties']['datetime'],j[0]['id']))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(process,jobs))
 print('COMPLETE',flush=True)
