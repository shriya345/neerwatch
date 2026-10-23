"""Isolated CyFi compatibility probe. No production or historical-job writes."""
import os,sys,json,hashlib,zipfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent/'cyfi'))
os.environ.setdefault('GDAL_HTTP_TIMEOUT','30')
os.environ.setdefault('GDAL_HTTP_MAX_RETRY','2')
import numpy as np,pandas as pd,requests,rioxarray,planetary_computer as pc
import lightgbm as lgb,yaml
from cyfi.config import FeaturesConfig
from cyfi.data.features import _calculate_satellite_features_for_sample_item,lookup_land_cover
from cyfi.data.satellite_data import get_bounding_box
from shapely.geometry import shape,Point
import xarray as xr

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 registry=ROOT/'data/reservoirs.json';before=sha(registry)
 reservoirs=json.loads(registry.read_text()); assert len(reservoirs)==46
 weights=BASE.parent/'cyfi/cyfi/assets/model_v0.zip'
 with zipfile.ZipFile(weights) as z:
  cfg=FeaturesConfig(**yaml.safe_load(z.read('features_config.yaml')))
  models=[lgb.Booster(model_str=z.read(n).decode()) for n in z.namelist() if n.startswith('lgb_model_')]
 manifest={'registry_sha256':before,'model_sha256':sha(weights),'models':len(models),'features':models[0].feature_name(),'results':[]}
 for rid in os.environ.get('CYFI_PROBE_IDS','krs,bhadra,tungabhadra').split(','):
  r=next(r for r in reservoirs if r['id']==rid)
  result={'reservoir_id':rid,'latitude':r['latitude'],'longitude':r['longitude'],'prediction_cells_per_ml':None,'locally_validated':False}
  try:
   boundary=json.loads((ROOT/f'data/boundaries/{rid}.geojson').read_text())
   if boundary['type']=='FeatureCollection': geom=shape(boundary['features'][0]['geometry'])
   elif boundary['type']=='Feature': geom=shape(boundary['geometry'])
   else: geom=shape(boundary)
   result['registry_point_inside_polygon']=geom.covers(Point(r['longitude'],r['latitude']))
   if not result['registry_point_inside_polygon']: raise ValueError('Registry point outside reservoir polygon; no guessed replacement')
   obs=sorted(json.loads((ROOT/f'data/sentinel2/{rid}/history.json').read_text()),key=lambda o:o['observed_at'])[-1]
   result.update(scene_id=obs['item_id'],acquisition_date=obs['observed_at'],source_url=obs['source_url'],requested_date=obs['observed_at'][:10])
   scene_file=BASE/f'{rid}-scene.json'
   if not scene_file.exists():
    response=requests.get(obs['source_url'],timeout=45);response.raise_for_status();scene_file.write_text(json.dumps(response.json(),indent=2))
   scene=json.loads(scene_file.read_text());result['processing_baseline']=scene['properties'].get('s2:processing_baseline')
   dest=BASE/f'sentinel_2000/{rid}/{scene["id"]}';dest.mkdir(parents=True,exist_ok=True)
   bounds=get_bounding_box(r['latitude'],r['longitude'],2000)
   result['sample_bbox']=bounds;result['band_files']={}
   # Exact upstream raw-DN crop, native grids; do not substitute NEERWATCH reflectances.
   for band in ['SCL']+[b for b in cfg.use_sentinel_bands if b!='SCL']:
    path=dest/f'{band}.npy'
    if not path.exists():
     href=pc.sign(scene['assets'][band]['href'])
     with rioxarray.open_rasterio(href) as a:
      values=a.rio.clip_box(minx=bounds[0],miny=bounds[1],maxx=bounds[2],maxy=bounds[3],crs='EPSG:4326').to_numpy()
     np.save(path,values)
    result['band_files'][band]={'sha256':sha(path),'source_url':scene['assets'][band]['href'].split('?')[0]}
    print(rid,band,'cached',flush=True)
   f=_calculate_satellite_features_for_sample_item(rid,scene['id'],cfg,BASE)
   result['cloud_fraction']=f.get('cloud_pct');result['water_pixels_upstream_last_band']=f.get('num_water_pixels')
   if not all(k in f and np.isfinite(f[k]) for k in cfg.satellite_image_features): raise ValueError('Upstream cloud/water/no-data QC did not produce all spectral features')
   f.update(month=int(obs['observed_at'][5:7]),days_before_sample=0)
   lc=BASE/'C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc'
   if not lc.exists():
    result['status']='BLOCKED_MISSING_LAND_COVER';result['reason']='Exact upstream 2020 C3S land-cover raster not yet available locally; no imputed feature or prediction.'
   else:
    with xr.open_dataset(lc) as d: f['land_cover']=int(lookup_land_cover(r['latitude'],r['longitude'],d))
    if f['land_cover'] <= 0: raise ValueError('Land-cover class missing or unknown; inference withheld')
    x=pd.DataFrame([f])[models[0].feature_name()]
    logdensity=np.mean([m.predict(x,num_threads=1)[0] for m in models])
    result['prediction_cells_per_ml']=float(np.round(np.expm1(max(0,logdensity))))
    result['status']='EXPERIMENTAL_UPSTREAM_INFERENCE_ONLY'
   pd.DataFrame([f]).to_csv(BASE/f'{rid}-features.csv',index=False)
   result['limitations']=['U.S.-trained; no Karnataka validation','4 km box may include other water; not a whole-reservoir estimate','Raw-DN processing baseline compatibility unresolved; not deployment approved','No FAI forecast, toxin estimate or health advisory']
  except Exception as e:
   result.update(status='BLOCKED',reason=f'{type(e).__name__}: {e}')
  manifest['results'].append(result)
  (BASE/os.environ.get('CYFI_RESULTS_FILE','results.json')).write_text(json.dumps(manifest,indent=2,default=str))
  print(rid,result['status'],result.get('reason',''),flush=True)
 assert sha(registry)==before
if __name__=='__main__': main()
