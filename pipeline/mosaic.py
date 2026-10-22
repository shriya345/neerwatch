"""Same-date/orbit/baseline Sentinel-2 mosaics. No temporal compositing."""
from datetime import datetime
from shapely.geometry import shape,mapping
from shapely.ops import unary_union

def observations(items,geometry):
 area=shape(geometry);groups={}
 for item in items:
  p=item['properties'];key=(p['datetime'][:10],p.get('platform'),p.get('sat:relative_orbit'),p.get('s2:processing_baseline'))
  groups.setdefault(key,[]).append(item)
 result=[]
 for key,tiles in groups.items():
  complete=[t for t in tiles if shape(t['geometry']).intersection(area).area/area.area>=.95]
  if complete:result.extend(complete);continue
  unique={}
  for t in sorted(tiles,key=lambda t:t['id'],reverse=True):unique.setdefault((t['properties'].get('s2:mgrs_tile') or t['id']),t)
  tiles=sorted(unique.values(),key=lambda t:t['id'])
  times=[datetime.fromisoformat(t['properties']['datetime'].replace('Z','+00:00')) for t in tiles]
  union=unary_union([shape(t['geometry']) for t in tiles]);coverage=union.intersection(area).area/area.area
  if len(tiles)<2 or coverage<.95 or (max(times)-min(times)).total_seconds()>300:
   result.extend(tiles);continue
  p=dict(tiles[0]['properties']);p['datetime']=min(times).isoformat().replace('+00:00','Z')
  rid='MOSAIC_'+str(p.get('platform','S2')).replace('-','')+'_'+min(times).strftime('%Y%m%dT%H%M%S')+'_'+str(p.get('sat:relative_orbit','orbit'))
  result.append({'id':rid,'properties':p,'geometry':mapping(union),'_mosaic_items':tiles,'_mosaic_time_difference_seconds':(max(times)-min(times)).total_seconds()})
 return sorted(result,key=lambda i:i['properties']['datetime'],reverse=True)
