"""Audit live API results against actual persisted Sentinel-2 spectral arrays."""
import json,time,os
from pathlib import Path
import httpx,numpy as np,rasterio
from scipy.ndimage import binary_erosion,binary_dilation
from backend.config import DATA,ROOT
from backend.epa import classify
BASE=os.environ.get('NEERWATCH_BASE_URL','http://127.0.0.1:8010')
IDS=[r['id'] for r in httpx.get(BASE+'/api/reservoirs',timeout=60).json()['items']]
OUTPUT=ROOT/'output';OUTPUT.mkdir(exist_ok=True)
with httpx.Client(base_url=BASE,timeout=60) as client:
 deadline=time.monotonic()+900
 while True:
  jobs={rid:client.get(f'/api/reservoirs/{rid}/processing').json() for rid in IDS}
  if all(j['status'] not in ('running','queued') for j in jobs.values()):break
  if time.monotonic()>deadline:raise TimeoutError('Live processing has not finished; do not report success.')
  time.sleep(5)
 report=[]
 for rid in IDS:
  response=client.get(f'/api/reservoirs/{rid}');response.raise_for_status();data=response.json()['sentinel2'];row=data['latest'];job=jobs[rid]
  result={'reservoir_id':rid,'processing_status':job['status'],'failure_reason':job.get('reason') if job['status']=='failed' else None,'scene_id':row['item_id'] if row else None,'acquisition_date':row['observed_at'] if row else None,'valid_water_pixels':row['quality']['valid_pixels'] if row else 0,'algorithm_valid_pixels':row['quality']['algorithm_valid_pixels'] if row else 0,'chlorophyll_a_ug_l':data['chlorophyll_a'],'algorithm':row['method'] if row else None,'epa_category':data['classification']['name'] if data['classification'] else None,'rejected_scenes':row.get('attempts',[]) if row else job.get('attempts',[]),'source_url':row['source_url'] if row else None}
  if data['chlorophyll_a'] is not None:
   directory=DATA/'sentinel2'/rid
   with np.load(directory/f"{row['item_id']}-bands.npz") as saved:
    b4=saved['B04'].astype('float64');b5=saved['B05'].astype('float64');valid=saved['valid_mask'];poly=saved['polygon_mask']
    with np.errstate(invalid='ignore',divide='ignore'):
     expected=(35.75*b5/b4-19.3)**1.124
    assert np.allclose(saved['chlorophyll_a'][valid],expected[valid],rtol=2e-5),rid
    median=float(np.median(expected[valid]));assert np.isclose(median,row['chlorophyll_a'],rtol=2e-5),rid
    assert int(valid.sum())==row['quality']['algorithm_valid_pixels'],rid
    assert classify(median)['name']==result['epa_category'],rid
    assert np.all(valid<=poly),rid
    if '_scl' in saved:
     scl=saved['_scl'];water=binary_erosion(poly&(scl==6),iterations=1)&~binary_dilation(np.isin(scl,[3,8,9,10]),iterations=1)
     for band in ['B02','B03','B04','B05','B08','B11']:
      a=saved[band];water &= np.isfinite(a)&(a>0)&(a<=1)
     expected_valid=water&np.isfinite(expected)&(expected>=1)&(expected<=100)
     assert np.array_equal(expected_valid,valid),rid
     result['water_cloud_reflectance_mask_verified']=True
    else:result['water_cloud_reflectance_mask_verified']=False
    with rasterio.open(directory/row['chlorophyll_raster_file']) as src:
     assert src.tags()['scene_id']==row['item_id'] and src.crs.to_epsg()==32643
     assert np.allclose(src.read(1)[valid],expected[valid],rtol=2e-5)
     result['analysis_crs']=str(src.crs);result['analysis_resolution_m']=src.res
   assert row['reservoir_id']==rid
   assert client.get(f'/api/reservoirs/{rid}/sentinel2/rgb').status_code==200
   assert client.get(f'/api/reservoirs/{rid}/sentinel2/chlorophyll').status_code==200
   result['independent_spectral_median_ug_l']=median;result['spectral_array_and_geotiff_verified']=True
   result['band_metadata']=row.get('spectral_bands',{})
  report.append(result)
 (OUTPUT/'processing-verification.json').write_text(json.dumps(report,indent=2,allow_nan=False))
 print(json.dumps([{k:r[k] for k in ['reservoir_id','processing_status','acquisition_date','valid_water_pixels','algorithm_valid_pixels','chlorophyll_a_ug_l','epa_category','failure_reason']} for r in report],indent=2),flush=True)
