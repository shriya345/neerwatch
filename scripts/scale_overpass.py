"""Retrieve original OSM water polygons near official dam points, never buffers."""
import json,time,re
import httpx
from shapely.geometry import Polygon,LineString,Point,mapping
from shapely.ops import polygonize,unary_union
from backend.config import DATA,write_json

def norm(s):return re.sub('[^a-z]','',s.lower())
def fetch(rid,name,gov):
 cache=DATA/'internal/scale-search'/f'{rid}-overpass.json';lat=gov['dam_latitude'];lon=gov['dam_longitude']
 if cache.exists():payload=json.loads(cache.read_text())
 else:
  query=f'[out:json][timeout:90];(way["natural"="water"](around:8000,{lat},{lon});relation["natural"="water"](around:8000,{lat},{lon});way["water"="reservoir"](around:8000,{lat},{lon});relation["water"="reservoir"](around:8000,{lat},{lon}););out body geom;'
  response=httpx.post('https://overpass-api.de/api/interpreter',data={'data':query},timeout=120,headers={'User-Agent':'NEERWATCH academic reservoir research'});response.raise_for_status();payload=response.json();write_json(cache,payload);time.sleep(2)
 matches=[]
 for e in payload.get('elements',[]):
  tags=e.get('tags',{});g=None
  try:
   if e['type']=='way':
    points=[(p['lon'],p['lat']) for p in e.get('geometry',[])]
    if len(points)>3 and points[0]==points[-1]:g=Polygon(points)
   elif e['type']=='relation':
    outer=[];inner=[]
    for member in e.get('members',[]):
     pts=[(p['lon'],p['lat']) for p in member.get('geometry',[]) if p]
     if len(pts)<2:continue
     (inner if member.get('role')=='inner' else outer).append(LineString(pts))
    g=unary_union(list(polygonize(unary_union(outer))))
    if inner:g=g.difference(unary_union(list(polygonize(unary_union(inner)))))
   if g is None or g.is_empty or not g.is_valid:continue
   distance=g.distance(Point(lon,lat))*111;area=g.area*111*111*__import__('math').cos(__import__('math').radians(lat))
   if area<.25 or distance>.3:continue
   named=any(norm(name) in norm(v) for k,v in tags.items() if k.startswith('name') and isinstance(v,str))
   if not (tags.get('water')=='reservoir' or named or distance<.05):continue
   matches.append((0 if tags.get('water')=='reservoir' else 1, distance,-area,e,g))
  except Exception:continue
 if not matches:return None
 matches.sort(key=lambda m:m[:3]);_,distance,_,e,g=matches[0]
 return {'geojson':mapping(g),'osm_type':e['type'],'osm_id':e['id'],'display_name':e.get('tags',{}).get('name',name)+' Reservoir, Karnataka','type':'reservoir','category':'water','tags':e.get('tags',{}),'government_dam_distance_approx_km':distance}
