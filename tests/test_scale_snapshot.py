import json,hashlib
from backend.config import DATA

def test_original_sixteen_cache_and_boundaries_unchanged():
 snapshot=json.loads((DATA/'internal/original-sixteen-scale-snapshot.json').read_text());assert len(snapshot)==16
 for paths in snapshot.values():
  for relative,digest in paths.items():assert hashlib.sha256((DATA/relative).read_bytes()).hexdigest()==digest

def test_real_mosaic_pixel_ownership_and_coverage():
 import numpy as np
 import rasterio
 for rid in ['basava-sagara','malaprabha']:
  root=DATA/'sentinel2'/rid;rows=json.loads((root/'history.json').read_text());assert len(rows)>=2
  for r in rows:
   if not r['item_id'].startswith('MOSAIC_'):continue
   assert r['mosaic_time_difference_seconds']<=300
   assert len({s['observed_at'][:10] for s in r['source_scenes']})==1
   assert r['quality']['footprint_fraction']>=.95 and r['quality']['data_footprint_fraction']>=.95
   with np.load(root/f"{r['item_id']}-bands.npz") as a:
    owners=a['_tile_index'];mask=a['valid_mask'];poly=a['polygon_mask']
    assert np.all(owners[mask]>=0) and np.all(owners[mask]<len(r['source_scenes']))
    counts=[int(((owners==i)&poly).sum()) for i in range(len(r['source_scenes']))]
    assert sum(counts)==int(((owners>=0)&poly).sum()) # every covered pixel owned exactly once
    b4=a['B04'][mask];b5=a['B05'][mask];expected=(35.75*b5/b4-19.3)**1.124
    assert np.allclose(a['chlorophyll_a'][mask],expected,rtol=2e-5)
    assert np.isclose(np.median(expected),r['chlorophyll_a'],rtol=2e-5)
