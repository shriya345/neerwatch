"""Government-matched candidate discovery; all results remain internal."""
import re,json,time,logging
from pathlib import Path
import httpx
from shapely.geometry import shape,Point
from backend.config import DATA,ROOT,write_json,today
SOURCE='https://www.cwc.gov.in/sites/default/files/nrld-2019.pdf'
# ID, display name, exact normalized government name prefix, optional query alias.
CANDIDATES=[('gerusoppa','Gerusoppa','gerusoppadam',''),('kodasalli','Kodasalli','kodasalli',''),('karanja','Karanja','karanjadam',''),('kanva','Kanva','kanvadam',''),('manchanabele','Manchanabele','manchanabele',''),('suvarnavathy','Suvarnavathy','suvarnavathydam','Suvarnavathi'),('taraka','Taraka','tarakadam',''),('votehole','Votehole','voteholedam','Vatehole'),('bennethora','Bennethora','bennithoradam','Bennithora'),('chandrampalli','Chandrampalli','chandrampallidam',''),('dharma','Dharma','dharmareservoir',''),('upper-tunga','Upper Tunga','uppertungadam','Gajanur'),('amarja','Amarja','amarjadam',''),('chikkahole','Chikkahole','chickkahole',''),('chiklihole','Chiklihole','chikliholedam','Chikli Hole'),('hattikuni','Hattikuni','hattikunidam','Hattikuni'),('narihalla','Narihalla','narihalladam',''),('upper-mullamari','Upper Mullamari','uppermullamaridam',''),('lower-mullamari','Lower Mullamari','lowermullamaridam',''),('gundal','Gundal','gundaldam',''),('gandorinala','Gandorinala','gandorinaladam','Gandori Nala'),('maskinala','Maskinala','maskinala','Maski'),('chulkinala','Chulkinala','chulkinaladam','Chulki Nala'),('harinala','Harinala','harinaladam',''),('hirehalla','Hirehalla','hirehalladam',''),('uduthorehalla','Uduthorehalla','uduthorehalladam','Uduthore Halla'),('jambhadhahalla','Jambhadhahalla','jambadahalladam','Jambadahalla'),('ambligola','Ambligola','ambligolatank',''),('tattihalla','Tattihalla','tattihalladam','Tattihalla'),('savehaklu','Savehaklu','savehakaludam','Savehaklu'),('chakra','Chakra','chakradam',''),('rakkaskop','Rakkaskop','rakkaskopdam','Rakaskop'),('gayathri','Gayathri','gayathrireservoir','Gayatri'),('talakalale','Talakalale','talakalaledam','Talakalele'),('thippagondanahalli','Thippagondanahalli','tippagondanahally','Tippagondanahalli'),('markandeya-reservoir','Markandeya','markandeyadam','Markandeya'),('kanakanala','Kanakanala','kanakanaladam','Kanaka Nala'),('neerasagara','Neerasagara','neerasagaradam','Neersagar'),('maralvadi','Maralvadi','maralvadidam','Maralawadi'),('arkavathy','Arkavathy','arkavathydam','Arkavathi'),('iggalur','Iggalur','iggalurdam','Iggalur')]
def norm(s):return re.sub('[^a-z]','',s.lower())
def inventory():
 result=[]
 for f in (ROOT.parent/'work').glob('nrld-karnataka-*.txt'):
  t=re.sub(r'KA(\d{2})(HH|MH|LH)\s*((?:\d\s*){4})',lambda m:'KA'+m[1]+m[2]+re.sub(r'\s','',m[3])+' ',f.read_text())
  for m in re.finditer(r'(KA\d{2}[A-Z]{2}\d{4})(.*?)(?=KA\d{2}[A-Z]{2}\d{4}|\Z)',t,re.S):
   b=' '.join(m[2].split());name=re.split(r'Karnatak',b)[0].strip();coords=list(re.finditer(r'(\d{1,3})°\s*(\d{1,2})\s*[\'’]\s*(\d{1,2}(?:\.\d+)?)\s*"',b))
   if len(coords)<2:continue
   lat,lon=[int(c[1])+int(c[2])/60+float(c[3])/3600 for c in coords[:2]]
   result.append({'inventory_id':m[1],'government_name':name,'normalized':norm(name),'government_source':SOURCE,'source_pdf_page':int(re.search(r'(\d+)\.txt',f.name)[1]),'dam_latitude':lat,'dam_longitude':lon,'government_excerpt':b[:400]})
 return result

def run():
 inv=inventory();pending=json.loads((DATA/'internal/pending-reservoirs.json').read_text());public=json.loads((DATA/'reservoirs.json').read_text());audit=[];cache=DATA/'internal/scale-search';cache.mkdir(exist_ok=True)
 with httpx.Client(timeout=40,follow_redirects=True,headers={'User-Agent':'NEERWATCH academic reservoir research (local project)'}) as client:
  for rid,name,prefix,alias in CANDIDATES:
   if any(r['id']==rid for r in public):continue
   matches=[i for i in inv if i['normalized'].startswith(prefix)];entry={'id':rid,'name':name}
   if len(matches)!=1:
    entry['reason']='No unique matching government dam record';audit.append(entry);write_json(DATA/'internal/scale-discovery-audit.json',audit);continue
   gov=matches[0];entry.update(gov);record=next((r for r in pending if r['id']==rid),None)
   boundary=DATA/'boundaries'/f'{rid}.geojson'
   if boundary.exists():
    feature=json.loads(boundary.read_text());polygon=shape(feature['geometry']);url=feature['properties']['source_url'];location=record.get('location','Karnataka') if record else 'Karnataka'
   else:
    candidates=[]
    for query in dict.fromkeys([name+' Reservoir Karnataka',(alias or name)+' Dam Karnataka']):
     cp=cache/(rid+'-'+norm(query)+'.json')
     if cp.exists():items=json.loads(cp.read_text())
     else:
      time.sleep(1.2)
      try:
       response=client.get('https://nominatim.openstreetmap.org/search',params={'q':query,'format':'jsonv2','polygon_geojson':1,'limit':5,'countrycodes':'in'});response.raise_for_status();items=response.json();write_json(cp,items)
      except Exception as exc:entry['search_error']=str(exc);continue
     for item in items:
      if item.get('geojson',{}).get('type') not in ['Polygon','MultiPolygon']:continue
      g=shape(item['geojson']);distance=g.distance(Point(gov['dam_longitude'],gov['dam_latitude']))*111
      if g.is_valid and distance<3 and item.get('class',item.get('category')) in ['natural','water','landuse'] and item.get('type')!='dam':
       candidates.append((distance,item))
     if candidates:break
    if not candidates:
     try:
      from scripts.scale_osm_api import fetch
      item=fetch(rid,name,gov)
      if item:candidates.append((item['government_dam_distance_approx_km'],item))
     except Exception as exc:entry['overpass_error']=str(exc)
    if not candidates:
     try:
      from scripts.scale_overpass import fetch as fetch_original
      item=fetch_original(rid,name,gov)
      if item:candidates.append((item['government_dam_distance_approx_km'],item))
     except Exception as exc:entry['osm_api_error']=str(exc)
    if not candidates:
     entry['reason']='No correct water polygon returned near government dam location';audit.append(entry);write_json(DATA/'internal/scale-discovery-audit.json',audit);print(rid,entry['reason'],flush=True);continue
    _,item=min(candidates,key=lambda x:x[0]);polygon=shape(item['geojson']);url=f"https://www.openstreetmap.org/{item['osm_type']}/{item['osm_id']}";location=item['display_name']
    feature={'type':'Feature','geometry':item['geojson'],'properties':{'name':name,'source_url':url,'retrieved_at':today().isoformat(),'retrieval_query':query,'osm_tags':item.get('tags',{}),'source_class':item.get('class'),'source_type':item.get('type'),'license':'© OpenStreetMap contributors, ODbL 1.0'}}
   distance=polygon.distance(Point(gov['dam_longitude'],gov['dam_latitude']))*111
   area=polygon.area*111*111*__import__('math').cos(__import__('math').radians(polygon.centroid.y))
   if not polygon.is_valid or distance>3 or area<.25:
    entry['reason']=f'Polygon verification failed: distance {distance:.2f} km; area {area:.3f} km²';audit.append(entry);write_json(DATA/'internal/scale-discovery-audit.json',audit);continue
   if 'tank' in gov['government_name'].lower():
    entry['reason']='Official name is Tank; independent substantial-reservoir classification not established';audit.append(entry);write_json(DATA/'internal/scale-discovery-audit.json',audit);continue
   # Avoid aliases/geometries overlapping existing operational reservoirs.
   duplicate=None
   for existing in public:
    g=shape(json.loads((DATA/'boundaries'/f"{existing['id']}.geojson").read_text())['geometry'])
    if g.intersection(polygon).area/min(g.area,polygon.area)>.6:duplicate=existing['id'];break
   if duplicate:entry['reason']='Duplicate water body of '+duplicate;audit.append(entry);continue
   write_json(boundary,feature);entry.update(identity_verified=True,boundary_source=url,distance_to_water_polygon_approx_km=distance,polygon_area_approx_km2=area)
   new={'id':rid,'name':name,'full_name':name+' Reservoir','state':'Karnataka','priority':False,'latitude':polygon.centroid.y,'longitude':polygon.centroid.x,'location':location,'district':None,'region':location,'source_url':url,'osm_url':url,'boundary_license':'© OpenStreetMap contributors, ODbL 1.0','boundary_available':True,'alternate_names':[alias] if alias else [],'identity_verification':entry,'pending_reasons':['Two processed comparable observations required']}
   pending=[r for r in pending if r['id']!=rid]+[new];write_json(DATA/'internal/pending-reservoirs.json',pending);audit.append(entry);write_json(DATA/'internal/scale-discovery-audit.json',audit);print(rid,'BOUNDARY VERIFIED',round(area,2),'km²',flush=True)
 write_json(DATA/'internal/scale-discovery-complete.json',{'complete':True,'count':len(audit)})
 return audit
if __name__=='__main__':run()
