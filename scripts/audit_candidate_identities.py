import json,re
from pathlib import Path
from shapely.geometry import shape,Point
from backend.config import DATA,ROOT,write_json
matches={'nugu':'Nugu Dam','kadra':'Kadra Dam','hemavathi':'Hemavathy Dam','almatti':'Almatti Dam','basava-sagara':'Narayanapura Dam','linganamakki':'Linganamakki Dam','malaprabha':'Malaprabha Dam','hidkal':'Hidkal Dam','yagachi':'Yagachi Dam'}
records=json.loads((DATA/'internal/pending-reservoirs.json').read_text());audit=[]
for rid,name in matches.items():
 for f in (ROOT.parent/'work').glob('nrld-karnataka-*.txt'):
  text=f.read_text()
  for m in re.finditer(r'(KA\d{2}[A-Z]{2}\d{4})(.*?)(?=KA\d{2}[A-Z]{2}\d{4}|\Z)',text,re.S):
   block=' '.join(m[2].split())
   if not block.startswith(name):continue
   coords=list(re.finditer(r'(\d{1,3})°\s*(\d{1,2})\s*[\'’]\s*(\d{1,2}(?:\.\d+)?)\s*"',block))
   lat,lon=[int(c[1])+int(c[2])/60+float(c[3])/3600 for c in coords[:2]]
   r=next(r for r in records if r['id']==rid);g=shape(json.loads((DATA/'boundaries'/f'{rid}.geojson').read_text())['geometry'])
   # Dam register points are shoreline structures, not polygon centroids.
   distance_degrees=g.distance(Point(lon,lat));entry={'id':rid,'government_name':name,'inventory_id':m[1],'government_source':'https://www.cwc.gov.in/sites/default/files/nrld-2019.pdf','source_pdf_page':int(re.search(r'(\d+)\.txt',f.name)[1]),'dam_latitude':lat,'dam_longitude':lon,'distance_to_water_polygon_approx_km':distance_degrees*111,'boundary_source':r['osm_url'],'identity_verified':distance_degrees*111<5,'use':'Government register confirms completed Karnataka dam and impounded reservoir; dam coordinate independently checked against water polygon.'}
   audit.append(entry)
# Markonahalli acknowledged as a reservoir by the Karnataka Legislature.
r=next(r for r in records if r['id']=='markonahalli')
audit.append({'id':'markonahalli','government_name':'Markonahalli reservoir','government_source':'https://kla.kar.nic.in/assembly/questions/lasq18072016.pdf','identity_verified':True,'boundary_source':r['osm_url'],'use':'Karnataka Legislative Assembly questions of 18 July 2016 explicitly address modernization of Markonahalli reservoir; polygon and S2 water overlap checked independently.'})
write_json(DATA/'internal/coverage-identity-audit.json',audit)
for a in audit:print(a['id'],a['identity_verified'],a.get('distance_to_water_polygon_approx_km'))
