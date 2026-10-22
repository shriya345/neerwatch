"""OSM original map/full XML fallback for unavailable Overpass service."""
import xml.etree.ElementTree as ET
import json,time
import httpx
from shapely.geometry import Point,Polygon,LineString,mapping
from shapely.ops import unary_union,polygonize
from backend.config import DATA

def fetch(rid,name,gov):
 lat=gov['dam_latitude'];lon=gov['dam_longitude'];cache=DATA/'internal/scale-search'/f'{rid}-osm-map.xml'
 with httpx.Client(timeout=60,follow_redirects=True,headers={'User-Agent':'NEERWATCH local academic reservoir research'}) as client:
  if cache.exists():content=cache.read_text()
  else:
   time.sleep(1.2);r=client.get('https://api.openstreetmap.org/api/0.6/map',params={'bbox':f'{lon-.025},{lat-.025},{lon+.025},{lat+.025}'});r.raise_for_status();content=r.text;cache.write_text(content)
  root=ET.fromstring(content);nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in root.findall('node')};ways={w.attrib['id']:w for w in root.findall('way')}
  def tags(e):return {t.attrib['k']:t.attrib['v'] for t in e.findall('tag')}
  def coords(w):return [nodes[n.attrib['ref']] for n in w.findall('nd') if n.attrib['ref'] in nodes]
  candidates=[]
  for w in ways.values():
   t=tags(w)
   if t.get('natural')!='water' and t.get('water')!='reservoir' and t.get('landuse')!='reservoir':continue
   pts=coords(w)
   if len(pts)>3 and pts[0]==pts[-1]:candidates.append(('way',w.attrib['id'],t,Polygon(pts)))
  for relation in root.findall('relation'):
   t=tags(relation)
   if t.get('natural')!='water' and t.get('water')!='reservoir' and t.get('landuse')!='reservoir':continue
   missing=any(m.attrib.get('type')=='way' and m.attrib['ref'] not in ways for m in relation.findall('member'))
   if missing:
    rc=DATA/'internal/scale-search'/f"osm-relation-{relation.attrib['id']}.xml"
    if rc.exists():full=ET.fromstring(rc.read_text())
    else:
     time.sleep(1.2);response=client.get(f"https://api.openstreetmap.org/api/0.6/relation/{relation.attrib['id']}/full");response.raise_for_status();rc.write_text(response.text);full=ET.fromstring(response.text)
    nodes.update({n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in full.findall('node')});ways.update({w.attrib['id']:w for w in full.findall('way')})
   outer=[];inner=[]
   for m in relation.findall('member'):
    if m.attrib.get('type')!='way' or m.attrib['ref'] not in ways:continue
    pts=coords(ways[m.attrib['ref']])
    if len(pts)>1:(inner if m.attrib.get('role')=='inner' else outer).append(LineString(pts))
   if outer:
    g=unary_union(list(polygonize(unary_union(outer))))
    if inner:g=g.difference(unary_union(list(polygonize(unary_union(inner)))))
    candidates.append(('relation',relation.attrib['id'],t,g))
 matches=[]
 for kind,oid,t,g in candidates:
  if not g.is_valid or g.is_empty:continue
  d=g.distance(Point(lon,lat))*111;area=g.area*111*111*__import__('math').cos(__import__('math').radians(lat))
  if d>.3 or area<.25:continue
  if not (t.get('water')=='reservoir' or t.get('landuse')=='reservoir' or name.lower() in t.get('name','').lower() or d<.05):continue
  matches.append((d,-area,kind,oid,t,g))
 if not matches:return None
 d,_,kind,oid,t,g=min(matches,key=lambda x:x[:2])
 return {'geojson':mapping(g),'osm_type':kind,'osm_id':oid,'display_name':t.get('name',name)+' Reservoir, Karnataka','type':'reservoir','category':'water','tags':t,'government_dam_distance_approx_km':d}
