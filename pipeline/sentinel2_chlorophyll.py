"""Actual Sentinel-2 L2A BOA -> experimental Gilerson 2B screening estimate.
Reuses WaterQual's NDCI and existing multiband/masking pipeline. Replaces
WaterQual's placeholder Gilerson model with the published power-law equation.
Sen2Cor BOA approximates aquatic reflectance; ACOLITE DSF is not claimed.
"""
import json,threading,logging
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from backend.config import DATA,today,write_json
from vendor.waterqual.indices import compute_ndci
from backend.epa import classify
SOURCE='https://doi.org/10.1364/OE.18.024109'
METHOD='Gilerson 2010 two-band; Sentinel-2 L2A BOA screening adaptation v1'
VALIDATION='Satellite-derived chlorophyll-a estimates have not yet been validated against Karnataka field measurements.'
JOBS={};PLOT_LOCK=threading.Lock();LOCK=threading.Lock();POOL=ThreadPoolExecutor(max_workers=2)
LOGGER=logging.getLogger("uvicorn.error")
LOOKBACK_DAYS=60
class ProcessingFailure(ValueError):
 def __init__(self,reason,attempts):
  super().__init__(reason);self.attempts=attempts
def get_status(identifier):
 if identifier in JOBS:return JOBS[identifier]
 path=DATA/"sentinel2"/identifier/"job.json"
 if path.exists():
  job=json.loads(path.read_text())
  if job["status"] in ("running","queued"):
   job.update(status="failed",stage="interrupted",reason="Processing was interrupted by a backend restart. Retry processing.")
   write_json(path,job)
  return job
 cached=DATA/"sentinel2"/identifier/"latest.json"
 if cached.exists():return {"status":"complete","reservoir_id":identifier,"result":json.loads(cached.read_text()),"cached":True}
 return {"status":"idle","reservoir_id":identifier}
def save_job(identifier,**changes):
 job={**JOBS.get(identifier,{}),**changes,"reservoir_id":identifier,"updated_at":datetime.now(timezone.utc).isoformat()}
 JOBS[identifier]=job;write_json(DATA/"sentinel2"/identifier/"job.json",job)
 return job
def gilerson(b05,b04):
 # Published expression also present in FCMm R/Chla_estimation.R.
 with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
  base=35.75*b05/b04-19.30;value=np.where((b04>0)&(b05>0)&(base>0),base**1.124,np.nan)
 # Conservative project screening domain, not clamping invalid outputs.
 return np.where(np.isfinite(value)&(value>=1)&(value<=100),value,np.nan).astype('float32')
def process(identifier,observations=1,progress=None):
 def emit(stage,**details):
  LOGGER.info("Sentinel-2 %s %s %s",identifier,stage,details.get("item_id",details.get("reason","")))
  if progress:progress(stage=stage,**details)
 from shapely.geometry import shape
 from pipeline.satellite import search,read_item,save_rgb
 from rasterio.warp import transform_geom
 from rasterio.transform import from_origin
 import rasterio
 records=json.loads((DATA/'reservoirs.json').read_text())
 pending=DATA/'internal/pending-reservoirs.json'
 if pending.exists():records+=json.loads(pending.read_text())
 record=next((r for r in records if r['id']==identifier),None)
 if record is None:raise ValueError('Unknown reservoir')
 boundary=DATA/'boundaries'/f'{identifier}.geojson'
 if not boundary.exists():raise ValueError('Verified water polygon required')
 geom=json.loads(boundary.read_text())['geometry']
 if not shape(geom).is_valid or shape(geom).area<=0:raise ValueError('Reservoir polygon is invalid or empty')
 emit('scene_search',lookback_days=LOOKBACK_DAYS)
 directory=DATA/'sentinel2'/identifier;directory.mkdir(parents=True,exist_ok=True)
 from pipeline.mosaic import observations as scene_observations
 items=scene_observations(search(geom,today(),lookback=LOOKBACK_DAYS,limit=60),geom)
 attempts=[];accepted=[];days=set();image_only=None
 emit("scenes_found",scene_count=len(items))
 for item in items:
  day=item['properties']['datetime'][:10]
  if day in days:continue
  emit('checking_scene',item_id=item['id'],acquisition_date=item['properties']['datetime'])
  coverage=shape(item['geometry']).intersection(shape(geom)).area/shape(geom).area
  if coverage<.95:
   attempts.append({'item_id':item['id'],'observed_at':item['properties']['datetime'],'stage':'footprint','reason':'Incomplete reservoir footprint','footprint_fraction':coverage});continue
  try:
   saved=directory/f"{item['id']}.json"
   if saved.exists():
    cached=json.loads(saved.read_text());required=['rgb_file','chlorophyll_map_file','chlorophyll_raster_file']
    if cached.get('chlorophyll_a') is not None and cached.get('method')==METHOD and cached.get('quality',{}).get('resolution_m')==60 and all(cached.get(k) and (directory/cached[k]).exists() for k in required):
     accepted.append(cached);days.add(day)
     if len(accepted)==1:write_json(directory/'latest.json',cached);emit('cached_scene',item_id=item['id'],result=cached)
     if len(accepted)>=observations:break
     continue
   result,bands,mask=read_item(item,geom,resolution=60,progress=lambda band:emit('reading_'+band,item_id=item['id'],acquisition_date=item['properties']['datetime']))
   if result['status']!='available':
    attempts.append({'item_id':item['id'],'observed_at':item['properties']['datetime'],'stage':'reflectance_quality','reason':result['reason'],'quality':result.get('quality')});continue
   valid=bands.pop('_valid_water_mask');emit('calculating_chlorophyll',item_id=item['id'],quality=result['quality']);ndci=compute_ndci(bands['B05'],bands['B04']);chl=gilerson(bands['B05'],bands['B04']);valid &= np.isfinite(chl)
   count=int(valid.sum());fraction=count/max(1,int(mask.sum()));chl[~valid]=np.nan;ndci[~valid]=np.nan
   centre=shape(geom).centroid;epsg=32600+int((centre.x+180)//6)+1;projected=shape(transform_geom('EPSG:4326',f'EPSG:{epsg}',geom));left,bottom,right,top=projected.bounds;transform=from_origin(left,top,60,60)
   prefix=item['id'];rgb=directory/f'{prefix}-rgb.png';save_rgb(bands,mask,rgb);ok=count>=25 and fraction>=.1
   manifest={'reservoir_id':identifier,'item_id':prefix,'observed_at':item['properties']['datetime'],'source':'Sentinel-2 L2A / Microsoft Planetary Computer','source_url':result['source_url'],'method':METHOD,'algorithm_source':SOURCE,'unit':'µg/L','spectral_bands':result.get('spectral_bands',{}),'source_scenes':[{'scene_id':t['id'],'observed_at':t['properties']['datetime'],'source_url':f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/{t['id']}"} for t in item.get('_mosaic_items',[item])],'mosaic_time_difference_seconds':item.get('_mosaic_time_difference_seconds',0),'chlorophyll_a':float(np.nanmedian(chl)) if ok else None,'status':'available' if ok else 'concentration_unavailable','quality_status':'experimental_screening','quality':{**result['quality'],'algorithm_valid_pixels':count,'algorithm_valid_fraction':fraction,'footprint_fraction':coverage,'algorithm_screening_range_ug_l':[1,100],'aggregation':'Median of valid per-pixel estimates'},'atmospheric_correction':'Provider Sen2Cor L2A BOA; aquatic DSF and adjacency correction not performed','limitation':'Published aquatic-reflectance algorithm applied to BOA as an experimental approximation. Concentration/category may be biased; not locally calibrated.','validation':VALIDATION,'rgb_file':rgb.name,'boundary_source':record.get('osm_url',record['source_url']),'processed_at':datetime.now(timezone.utc).isoformat(),'ndci_median':float(np.nanmedian(ndci)) if count else None,'attempts':attempts,'epa_category':classify(float(np.nanmedian(chl))) if ok else None}
   np.savez_compressed(directory/f'{prefix}-bands.npz',**bands,valid_mask=valid,polygon_mask=mask,ndci=ndci,chlorophyll_a=chl)
   if ok:
    tif=directory/f'{prefix}-chlorophyll.tif'
    with rasterio.open(tif,'w',driver='GTiff',height=chl.shape[0],width=chl.shape[1],count=1,dtype='float32',crs=f'EPSG:{epsg}',transform=transform,nodata=np.nan,compress='deflate') as dst:dst.write(chl,1);dst.update_tags(unit='ug/L',scene_id=prefix,algorithm=METHOD)
    with PLOT_LOCK:
