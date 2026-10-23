"""Read-only comparison: locked rioxarray crop against previously cached native DN."""
import os,json
from pathlib import Path
import numpy as np,rioxarray,planetary_computer as pc
BASE=Path(__file__).resolve().parent
rows=json.loads((BASE/'verification-five-results.json').read_text())['results'];checks=[]
for row in rows:
 if row['reservoir_id'] not in ['krs','bhadra','supa']:continue
 scene=json.loads((BASE/f"{row['reservoir_id']}-scene.json").read_text());b=row['sample_bbox']
 for band in ['B04','SCL']:
  with rioxarray.open_rasterio(pc.sign(scene['assets'][band]['href'])) as src:
   a=src.rio.clip_box(minx=b[0],miny=b[1],maxx=b[2],maxy=b[3],crs='EPSG:4326').to_numpy()
  old=np.load(BASE/f"sentinel_2000/{row['reservoir_id']}/{scene['id']}/{band}.npy")
  assert np.array_equal(a,old)
  checks.append({'reservoir_id':row['reservoir_id'],'band':band,'exact_native_crop_match':True,'shape':list(a.shape)})
(BASE.parents[2]/'output/cyfi-final-verification/locked-crop-checks.json').write_text(json.dumps(checks,indent=2))
print(checks)
