"""Run: python -m pipeline.collect --reservoir bhadra --months 3"""
import argparse,json,time
from datetime import timedelta,datetime,timezone
import httpx
from backend.config import DATA,today,write_json
from pipeline.satellite import acquire,save_rgb
from backend.weather_quality import screen_weather

def weather(record,start,end):
    params={'parameters':'T2M,PRECTOTCORR,WS2M','community':'AG','latitude':record['latitude'],'longitude':record['longitude'],'start':start.strftime('%Y%m%d'),'end':end.strftime('%Y%m%d'),'format':'JSON'}
    with httpx.Client(timeout=70,follow_redirects=True) as c:
        r=c.get('https://power.larc.nasa.gov/api/temporal/daily/point',params=params);r.raise_for_status();payload=r.json()
    if payload.get('parameters',{}).get('PRECTOTCORR',{}).get('units')!='mm/day':raise ValueError('Unexpected precipitation units; no implicit conversion applied.')
    variables=payload['properties']['parameter'];dates=sorted(variables['T2M'])
    rows=[]
    for day in dates:
        row={'date':f'{day[:4]}-{day[4:6]}-{day[6:]}'}
        for source,target in [('T2M','air_temperature_c'),('PRECTOTCORR','rainfall_mm'),('WS2M','wind_speed_ms')]:
            value=variables[source].get(day)
            row[target]=value if value is not None and value!=-999 else None
        rows.append(screen_weather(row))
    return {'source':'NASA POWER daily gridded meteorology (not an in-lake measurement)','source_url':str(r.url),'retrieved_at':datetime.now(timezone.utc).isoformat(),'rows':rows,'parameters':payload.get('parameters',{})}

def collect(record,months=3):
    path=DATA/'observations'/f"{record['id']}.json"
    stored=json.loads(path.read_text()) if path.exists() else {'reservoir_id':record['id'],'observations':[]}
    end=today()-timedelta(days=7)
    try:
        stored['weather']=weather(record,end-timedelta(days=months*30),end)
        stored.pop('weather_error',None)
    except Exception as exc:stored['weather_error']=f'{type(exc).__name__}: {str(exc)[:200]}'
    write_json(path,stored)
    boundary=DATA/'boundaries'/f"{record['id']}.geojson"
    if not boundary.exists():return
    geom=json.loads(boundary.read_text())['geometry']
    for index in range(months):
        day=end-timedelta(days=index*30)
        print(record['id'],day,flush=True)
        try:
            observation,arrays,mask=acquire(geom,day,lookback=20)
            observation['query_end']=day.isoformat()
            observation['boundary_source']=json.loads(boundary.read_text()).get('properties',{}).get('source_url','Mapped reservoir polygon; see stored GeoJSON provenance')
            if arrays is not None:
                image=DATA/'observations'/f"{record['id']}-{observation['observed_at'][:10]}.png"
                save_rgb(arrays,mask,image);observation['image_filename']=image.name
        except Exception as exc:
            observation={'status':'source_unavailable','query_end':day.isoformat(),'observed_at':None,'features':None,'reason':f'{type(exc).__name__}: {str(exc)[:180]}'}
        existing={o.get('query_end'):o for o in stored['observations']}
        existing[observation['query_end']]=observation
        stored['observations']=sorted(existing.values(),key=lambda x:x.get('query_end',''))
        stored['updated_at']=datetime.now(timezone.utc).isoformat()
        write_json(path,stored)
        print(record['id'],observation['status'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reservoir',default='priority');p.add_argument('--months',type=int,default=3);args=p.parse_args()
    records=json.loads((DATA/'reservoirs.json').read_text())
    for record in records:
        if (args.reservoir=='priority' and record['priority'] or args.reservoir=='extended' and not record['priority'] or record['id']==args.reservoir) and record.get('boundary_available'):
            collect(record,args.months)
