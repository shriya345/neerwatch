"""Bounded, resumable original CyFi acquisition. Writes only its own cache/report.
Frozen 2026-10-23 cutoff; up to 8 distinct dates per reservoir in 120 days.
Original eight manifest records are never candidates. No historical FAI writes.
"""
import os,sys,json,time,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'output/cyfi-coverage-expansion';CACHE=BASE/'coverage-cache';CACHE.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE.parent/'cyfi'))
os.environ.setdefault('GDAL_HTTP_TIMEOUT','30');os.environ.setdefault('GDAL_HTTP_MAX_RETRY','2')
import numpy as np,pandas as pd,requests,rioxarray,planetary_computer as pc,lightgbm as lgb,yaml,xarray as xr
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from shapely.geometry import shape,Point,mapping
from cyfi.config import FeaturesConfig
from cyfi.data.features import _calculate_satellite_features_for_sample_item,lookup_land_cover
from cyfi.data.satellite_data import get_bounding_box
URL='https://planetarycomputer.microsoft.com/api/stac/v1'
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2,default=lambda v:v.item() if hasattr(v,'item') else str(v),allow_nan=False));tmp.replace(p)
def retry(fn):
 for attempt in range(3):
  try:return fn()
  except Exception:
   if attempt==2:raise
   time.sleep(2**(attempt+1))
def get(url,params=None):
 def call():
  r=requests.get(url,params=params,timeout=45);r.raise_for_status();return r.json()
 return retry(call)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(ROOT/'models/cyfi/model_v0.zip') as z:
 cfg=FeaturesConfig(**yaml.safe_load(z.read('features_config.yaml')))
 models=[lgb.Booster(model_str=z.read(n).decode()) for n in sorted(z.namelist()) if n.startswith('lgb_model_')]
assert len(models)==5
before=json.loads((OUT/'inputs-before.json').read_text());registry=json.loads((ROOT/'data/reservoirs.json').read_text())
assert sha(ROOT/'data/reservoirs.json')==before['registry_sha256']
def inspect(r,scene,geom):
 rid=r['id'];sid=scene['id'];dest=BASE/f'sentinel_2000/{rid}/{sid}';dest.mkdir(parents=True,exist_ok=True)
 row=dict(reservoir_id=rid,latitude=r['latitude'],longitude=r['longitude'],locally_validated=False,registry_point_inside_polygon=True,scene_id=sid,acquisition_date=scene['properties']['datetime'],source_url=f'{URL}/collections/sentinel-2-l2a/items/{sid}',processing_baseline=scene['properties'].get('s2:processing_baseline'),cache_base=str(BASE.relative_to(ROOT)),band_files={})
 bounds=get_bounding_box(r['latitude'],r['longitude'],2000);row['sample_bbox']=bounds
 for band in ['SCL']+[b for b in cfg.use_sentinel_bands if b!='SCL']:
  if band not in scene['assets']:raise ValueError(f'Missing required asset {band}')
  p=dest/f'{band}.npy';meta=dest/f'{band}-grid.json'
  def download():
   with rioxarray.open_rasterio(pc.sign(scene['assets'][band]['href'])) as src:
    crop=src.rio.clip_box(minx=bounds[0],miny=bounds[1],maxx=bounds[2],maxy=bounds[3],crs='EPSG:4326');arr=crop.to_numpy();grid={'crs':str(crop.rio.crs),'transform':list(crop.rio.transform()),'shape':list(arr.shape)}
   if not p.exists():
    tmp=p.with_suffix('.tmp');f=open(tmp,'wb');np.save(f,arr);f.close();tmp.replace(p)
   save(meta,grid)
  if not p.exists() or not meta.exists():retry(download)
  row['band_files'][band]={'sha256':sha(p),'source_url':scene['assets'][band]['href'].split('?')[0]}
  if band=='SCL':
   from affine import Affine
   scl=np.load(p)[0];grid=json.loads(meta.read_text());water=scl==6
   cloud=float(((scl>=7)&(scl<=10)).mean());row['cloud_fraction']=cloud
   mask=geometry_mask([transform_geom('EPSG:4326',grid['crs'],mapping(geom))],out_shape=scl.shape,transform=Affine(*grid['transform'][:6]),invert=True)
   row['water_pixels']=int(water.sum());row['inside_fraction']=float((water&mask).sum()/water.sum()) if water.any() else 0
   if cloud>.05:raise ValueError(f'Cloud fraction {cloud:.4%} exceeds original 5% limit')
   if row['inside_fraction']<.95:raise ValueError(f'Only {row["inside_fraction"]:.4%} of SCL water belongs to reservoir polygon; minimum 95%')
 f=_calculate_satellite_features_for_sample_item(rid,sid,cfg,BASE)
 invalid=[k for k in cfg.satellite_image_features if k not in f or not np.isfinite(f[k])]
 if invalid:raise ValueError('Original feature QC missing/nonfinite: '+', '.join(invalid))
 with xr.open_dataset(BASE/'C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc') as d:lc=int(lookup_land_cover(r['latitude'],r['longitude'],d))
 if lc<=0:raise ValueError('Missing land-cover lookup')
 row['land_cover']=lc;f.update(month=int(row['acquisition_date'][5:7]),days_before_sample=0,land_cover=lc)
 x=pd.DataFrame([f])[models[0].feature_name()]
 if not np.isfinite(x.to_numpy()).all():raise ValueError('Nonfinite model inputs')
 logs=[float(m.predict(x,num_threads=1)[0]) for m in models];density=float(np.round(np.expm1(max(0,float(np.mean(logs))))))
 if not np.isfinite(density):raise ValueError('Nonfinite prediction')
 row.update(status='eligible',limitations=['Experimental; no Karnataka field validation','Raw-DN radiometric transfer and out-of-training-range inputs remain unresolved','4 km box, not whole-reservoir mean; no toxin or FAI forecast'])
 return row,dict(density_cells_per_ml=density,fold_log_predictions=logs,features={k:float(f[k]) for k in models[0].feature_name()})
def run(r):
 rid=r['id'];progress=OUT/f'checkpoints/{rid}.json'
 if progress.exists():
  previous=json.loads(progress.read_text())
  if previous.get('approved') or (previous.get('finished') and not os.environ.get('CYFI_SECOND_PASS')):return
 state=json.loads(progress.read_text()) if progress.exists() else {'reservoir_id':rid,'attempts':[],'finished':False}
 state['finished']=False
 try:
  gj=json.loads((ROOT/f'data/boundaries/{rid}.geojson').read_text());geom=shape(gj['features'][0]['geometry'] if gj['type']=='FeatureCollection' else gj['geometry'] if gj['type']=='Feature' else gj)
  if not geom.is_valid or not geom.covers(Point(r['longitude'],r['latitude'])):raise ValueError('Invalid boundary or registry point outside polygon; no replacement point guessed')
  history=json.loads((ROOT/f'data/sentinel2/{rid}/history.json').read_text());candidates=[]
  for o in sorted(history,key=lambda x:x['observed_at'],reverse=True):
   if o['item_id'].startswith('S2'):candidates.append((o['item_id'],o['source_url']))
  seen=set(a['scene_id'] for a in state['attempts']);dates=set();count=0
  def try_candidates(candidates):
   nonlocal count
   for sid,url in candidates:
    if sid in seen or count>=8:continue
    date=sid.split('_')[2][:8]
    if date in dates:continue
    dates.add(date);seen.add(sid);count+=1
    attempt={'scene_id':sid,'source_url':url}
    try:
     sf=CACHE/f'{sid}.json'
     if not sf.exists():save(sf,get(url))
     scene=json.loads(sf.read_text());attempt['acquisition_date']=scene['properties']['datetime']
     if not '2026-06-25'<=attempt['acquisition_date'][:10]<='2026-10-23':raise ValueError('Outside documented 120-day search window')
     row,pred=inspect(r,scene,geom);state.update(approved=row,inference=pred,finished=True);attempt['status']='approved'
    except Exception as e:attempt.update(status='rejected',reason=str(e))
    state['attempts'].append(attempt);save(progress,state);print(rid,sid,attempt['status'],attempt.get('reason',''),flush=True)
    if state.get('approved'):return True
   return False
  if try_candidates(candidates):return
  cat=CACHE/f'{rid}-catalogue.json'
  if not cat.exists():
   payload=get(URL+'/search',{'collections':'sentinel-2-l2a','bbox':f'{r["longitude"]-.0001},{r["latitude"]-.0001},{r["longitude"]+.0001},{r["latitude"]+.0001}','datetime':'2026-06-25T00:00:00Z/2026-10-23T23:59:59Z','limit':100,'sortby':'-properties.datetime'});save(cat,payload)
  scenes=json.loads(cat.read_text()).get('features',[])
  for scene in scenes:save(CACHE/f'{scene["id"]}.json',scene)
  try_candidates([(s['id'],f'{URL}/collections/sentinel-2-l2a/items/{s["id"]}') for s in sorted(scenes,key=lambda s:(s['properties'].get('eo:cloud_cover',100)>20, ''.join(chr(255-ord(c)) for c in s['properties']['datetime'])) if os.environ.get('CYFI_SECOND_PASS') else s['properties']['datetime'],reverse=not bool(os.environ.get('CYFI_SECOND_PASS')))])
  state['catalogue_count']=len(scenes);state['catalogue_has_more']=any(l.get('rel')=='next' for l in json.loads(cat.read_text()).get('links',[]));state['finished']=True
 except Exception as e:state.update(finished=True,reason=str(e))
 save(progress,state)
for r in sorted(registry,key=lambda r:before['records'][r['id']]['status']=='rejected'):
 if before['records'][r['id']]['status']=='eligible':continue
 run(r)
