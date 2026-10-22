"""Public inventory gate: persisted, comparable, same-acquisition evidence only."""
import json,math
from functools import lru_cache
from shapely.geometry import shape,Point
from backend.config import DATA
from backend.epa import classify

def compatible(a,b):
 keys=['resolution_m','shoreline_buffer_m','cloud_buffer_m','minimum_valid_pixels','minimum_valid_fraction','algorithm_screening_range_ug_l','aggregation']
 return a.get('method')==b.get('method') and a.get('atmospheric_correction')==b.get('atmospheric_correction') and all(a.get('quality',{}).get(k)==b.get('quality',{}).get(k) for k in keys)

def check(record):
 rid=record['id'];root=DATA/'sentinel2'/rid
 paths=[DATA/'boundaries'/f'{rid}.geojson',root/'latest.json',root/'history.json']
 paths+=list(root.glob('*-bands.npz'))+list(root.glob('*-rgb.png'))+list(root.glob('*-chlorophyll.png'))+list(root.glob('*-chlorophyll.tif'))
 signature=tuple((str(p),p.stat().st_mtime_ns,p.stat().st_size) if p.exists() else (str(p),None,None) for p in paths)
 return _checked(json.dumps(record,sort_keys=True),signature)

@lru_cache(maxsize=128)
def _checked(record_json,signature):
 record=json.loads(record_json)
 from backend.active import monitoring
 errors=[];rid=record['id'];root=DATA/'sentinel2'/rid
 try:
  if not record.get('boundary_available') or not record.get('osm_url'):raise ValueError('Verified water boundary provenance required')
  boundary=json.loads((DATA/'boundaries'/f'{rid}.geojson').read_text());g=shape(boundary['geometry'])
  if not g.is_valid or g.is_empty or g.geom_type not in ['Polygon','MultiPolygon']:raise ValueError('Invalid water polygon')
  if not g.buffer(.01).covers(Point(record['longitude'],record['latitude'])):raise ValueError('Location does not match polygon')
  if not (11<g.centroid.y<19 and 73<g.centroid.x<79):raise ValueError('Outside Karnataka region')
 except (OSError,ValueError,KeyError) as exc:errors.append(str(exc))
 m=monitoring(rid);latest=m['latest'];previous=m['previous']
 if not latest or not previous or not m['change']:errors.append('Two valid comparable acquisitions required')
 for row in [latest,previous]:
  if not row:continue
  value=row.get('chlorophyll_a')
  if value is None or not math.isfinite(value) or value<=0 or not classify(value):errors.append('Invalid concentration')
  if row.get('reservoir_id')!=rid or not row.get('source_url') or not row.get('observed_at') or not row.get('method'):errors.append('Missing/mismatched provenance')
  if not (root/f"{row['item_id']}-bands.npz").is_file():errors.append('Missing source spectral arrays')
  if row.get('unit')!='µg/L':errors.append('Missing or incorrect concentration units')
  for key in ['rgb_file','chlorophyll_map_file','chlorophyll_raster_file']:
   name=row.get(key,'')
   if not name or not name.startswith(row['item_id']) or not (root/name).is_file():errors.append('Missing or mismatched '+key)
 if latest and previous and (not compatible(latest,previous) or latest['observed_at'][:10]==previous['observed_at'][:10]):errors.append('Incompatible observation pair')
 return {'ready':not errors,'reasons':errors}
