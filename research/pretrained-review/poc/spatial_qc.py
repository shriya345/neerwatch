from pathlib import Path
import json,os,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
sys.path.insert(0,str(BASE.parent/'cyfi'))
import numpy as np, rioxarray, planetary_computer as pc
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from shapely.geometry import shape,Point,mapping
from cyfi.data.satellite_data import get_bounding_box
out=[]
for r in json.loads((ROOT/'data/reservoirs.json').read_text()):
 if r['id'] not in os.environ.get('CYFI_PROBE_IDS','krs,bhadra,tungabhadra').split(','): continue
 rid=r['id'];s=json.loads((BASE/f'{rid}-scene.json').read_text())
 b=get_bounding_box(r['latitude'],r['longitude'],2000)
 with rioxarray.open_rasterio(pc.sign(s['assets']['SCL']['href'])) as src:
  crop=src.rio.clip_box(minx=b[0],miny=b[1],maxx=b[2],maxy=b[3],crs='EPSG:4326')
  transform=crop.rio.transform();crs=crop.rio.crs
  scl=np.load(BASE/f'sentinel_2000/{rid}/{s["id"]}/SCL.npy')[0]
  gj=json.loads((ROOT/f'data/boundaries/{rid}.geojson').read_text())
  if gj['type']=='FeatureCollection': gj=gj['features'][0]['geometry']
  elif gj['type']=='Feature': gj=gj['geometry']
  mask=geometry_mask([transform_geom('EPSG:4326',crs,gj)],out_shape=scl.shape,transform=transform,invert=True)
  water=scl==6; inside=int((water&mask).sum());total=int(water.sum())
  out.append(dict(reservoir_id=rid,scene_id=s['id'],scl_water_pixels=total,water_pixels_inside_polygon=inside,water_pixels_outside_polygon=total-inside,inside_fraction=inside/total if total else None,crs=str(crs),transform=list(transform),note='Diagnostic only. Upstream model retains its own unmodified box mask; no local validation.'))
(BASE/os.environ.get('CYFI_SPATIAL_FILE','spatial-qc.json')).write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
