"""Retrieve genuine official OLCI CHL_NN concentrations, including inland water.
Decode NetCDF packing THEN invert log10, verify source MD5s, use geolocation
arrays (not a guessed raster transform), and read WQSF masks from file metadata.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import httpx,numpy as np
from netCDF4 import Dataset
from shapely.geometry import shape
from shapely import contains_xy
from shapely.ops import transform
from pyproj import Transformer
from backend.config import DATA,write_json,today
from backend.monitoring import reservoirs
COLLECTION='sentinel-3-olci-wfr-l2-netcdf'
STAC='https://planetarycomputer.microsoft.com/api/stac/v1'
MANUAL='https://earth.esa.int/eogateway/documents/20142/1564943/Sentinel-3-OLCI-Marine-User-Handbook.pdf'
REJECT=['INVALID','CLOUD','CLOUD_AMBIGUOUS','CLOUD_MARGIN','SNOW_ICE','COSMETIC','SUSPECT','HISOLZEN','SATURATED','HIGHGLINT','WHITECAPS','ADJAC','AC_FAIL','OCNN_FAIL']
METHOD='Sentinel-3 OLCI official CHL_NN; median of screened 300 m interior-water pixels'
NOTE='Satellite-derived estimate from the official Sentinel-3 neural-network water product; not a field measurement. A 300 m shoreline buffer and inland-water, cloud, glint, saturation, atmospheric/NN failure flags are screened. Karnataka field accuracy is not established. Spatial coverage and source flags are retained.'

def decode_chlorophyll(variable,window):
    if variable.units!='lg(re mg.m-3)':raise ValueError(f'Unexpected chlorophyll unit {variable.units}')
    # netCDF4 applies scale_factor/add_offset and masks _FillValue by default.
    log=variable[window];return np.asarray(np.ma.filled(10.**log,np.nan),dtype=float)

def download(item,cache,token,keys):
    dest=cache/item['id'];dest.mkdir(parents=True,exist_ok=True)
    def get(key):
        asset=item['assets'][key];target=dest/(key+'.nc')
        if not target.exists():
            with httpx.Client(timeout=120) as client:
                r=client.get(asset['href']+'?'+token);r.raise_for_status();target.write_bytes(r.content)
        expected=asset.get('file:checksum')
        if not expected or hashlib.md5(target.read_bytes()).hexdigest()!=expected:raise ValueError(f'Source checksum mismatch {key}')
        return target
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,keys))
    write_json(dest/'item.json',item)
    return dest

def extract(item,dest,records):
    # Read a broad regional window located from actual swath geolocation.
    with Dataset(dest/'geo-coordinates.nc') as ds:
        lat0=ds['latitude'][::32,::32];lon0=ds['longitude'][::32,::32]
        region=(lat0>=11.5)&(lat0<=17.5)&(lon0>=73.5)&(lon0<=78.5)
        rr,cc=np.where(region)
        if not len(rr):return [],[]
        rs=slice(max(0,int(rr.min())*32-64),int(rr.max())*32+65);cs=slice(max(0,int(cc.min())*32-64),int(cc.max())*32+65);window=(rs,cs)
        lat=np.asarray(ds['latitude'][window]);lon=np.asarray(ds['longitude'][window])
    with Dataset(dest/'wqsf.nc') as ds:
        variable=ds['WQSF'];q=np.asarray(variable[window],dtype=np.uint64);flags=dict(zip(variable.flag_meanings.split(),map(int,variable.flag_masks)))
    if not all(k in flags for k in REJECT+['INLAND_WATER']):raise ValueError('Required provider flag metadata missing')
    rejected=np.uint64(sum(flags[k] for k in REJECT));validflags=((q&rejected)==0)&((q&np.uint64(flags['INLAND_WATER']))!=0)
    with Dataset(dest/'chl-nn.nc') as ds:
        v=ds['CHL_NN'];chl=decode_chlorophyll(v,window);packing={k:str(v.getncattr(k)) for k in v.ncattrs()}
    valid=validflags&np.isfinite(chl)&(chl>0)
    tr=Transformer.from_crs(4326,32643,always_xy=True);x,y=tr.transform(lon,lat);rows=[];audit=[]
    for record in records:
        geometry=shape(json.loads((DATA/'boundaries'/f"{record['id']}.geojson").read_text())['geometry'])
        interior=transform(tr.transform,geometry).buffer(-300)
        mask=contains_xy(interior,x,y);use=mask&valid;count=int(use.sum());total=int(mask.sum());coverage=count/total if total else 0
        histogram={k:int((mask&((q&np.uint64(v))!=0)).sum()) for k,v in flags.items() if k in REJECT+['INLAND_WATER','LAND','WATER']}
        footprint=transform(tr.transform,shape(item['geometry']));footprint_fraction=interior.intersection(footprint).area/interior.area if interior.area else 0
        entry={'footprint_fraction':footprint_fraction,'reservoir_id':record['id'],'item_id':item['id'],'observed_at':item['properties']['datetime'],'interior_pixels':total,'valid_pixels':count,'valid_fraction':coverage,'flag_counts':histogram,'accepted':count>=3 and coverage>=.1 and footprint_fraction>=.95};audit.append(entry)
        if not entry['accepted']:continue
        pixel_dir=DATA/'chlorophyll-pixels'/record['id'];pixel_dir.mkdir(parents=True,exist_ok=True)
        pixel_file=pixel_dir/f"{item['id']}.npz";np.savez_compressed(pixel_file,latitude=lat[mask],longitude=lon[mask],chlorophyll_a=chl[mask],wqsf=q[mask],accepted=valid[mask])
        row={'reservoir_id':record['id'],'observed_at':item['properties']['datetime'][:10],'chlorophyll_a':float(np.median(chl[use])),'unit':'µg/L','source':'Copernicus Sentinel-3 OLCI WFR Level-2 CHL_NN via Microsoft Planetary Computer','source_url':f"{STAC}/collections/{COLLECTION}/items/{item['id']}",'method':METHOD,'quality_status':'screened_satellite_estimate','quality_note':NOTE,'cyanobacteria_dominance_established':False,'quality':{**entry,'rejected_flags':REJECT,'flag_masks':flags,'shoreline_exclusion_m':300,'screening_min_pixels':3,'screening_min_fraction':.1,'provider_manual':MANUAL},'source_item':item['id'],'source_assets':{k:{'href':item['assets'][k]['href'],'md5':item['assets'][k]['file:checksum'],'checksum_verified':True} for k in ['geo-coordinates','chl-nn','wqsf']},'encoding':packing,'decode':'netCDF scale_factor/add_offset followed by 10**value; mg/m³ equals µg/L','pixel_file':str(pixel_file.relative_to(DATA)),'forecast_training_eligible':False,'retrieved_at':datetime.now(timezone.utc).isoformat(),'spatial_iqr_ug_l':list(map(float,np.percentile(chl[use],[25,75])))}
        rows.append(row)
    return rows,audit

def collect(limit=30,per_reservoir=2):
    records=[r for r in reservoirs() if not r['priority']];cache=DATA/'cache/sentinel3';cache.mkdir(parents=True,exist_ok=True)
    # Reuse only original source assets already fetched by the new project.
    probe=DATA/'satellite-originals/sentinel3'
    if probe.exists():
        for p in probe.iterdir():
            if not (cache/p.name).exists():shutil.move(str(p),cache/p.name)
    histories={r['id']:[] for r in records};audit=[];errors=[]
    with httpx.Client(timeout=60) as client:
        response=client.get(STAC+'/search',params={'collections':COLLECTION,'bbox':'74,12,78,17','limit':limit,'sortby':'-datetime','datetime':'../'+today().isoformat()+'T23:59:59Z'});response.raise_for_status();items=response.json()['features']
        t=client.get('https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel3euwest/sentinel-3');t.raise_for_status();token=t.json()['token']
    write_json(DATA/'sentinel3-catalogue-search.json',{'query_bbox':[74,12,78,17],'sorted':'datetime descending','items':items,'queried_at':datetime.now(timezone.utc).isoformat()})
    for index,item in enumerate(items):
        pending=[r for r in records if len(histories[r['id']])<per_reservoir and not any(o['observed_at']==item['properties']['datetime'][:10] for o in histories[r['id']]) and shape(item['geometry']).intersects(shape(json.loads((DATA/'boundaries'/f"{r['id']}.geojson").read_text())['geometry']))]
        if not pending:continue
        try:
            dest=download(item,cache,token,['geo-coordinates','chl-nn','wqsf']);rows,attempts=extract(item,dest,pending);audit+=attempts
            for row in rows:
                histories[row['reservoir_id']].append(row)
                path=DATA/'observations'/f"{row['reservoir_id']}-chlorophyll.json"
                existing=json.loads(path.read_text()) if path.exists() else []
                existing=[r for r in existing if r.get('source_item')!=row['source_item']];existing.append(row);write_json(path,sorted(existing,key=lambda r:r['observed_at']))
            print(index+1,item['properties']['datetime'],{k:len(v) for k,v in histories.items()},flush=True)
        except Exception as e:errors.append({'item_id':item['id'],'error':str(e)});print('Retrieval error',item['id'],type(e).__name__,flush=True)
        write_json(DATA/'sentinel3-acquisition-audit.json',{'collection':COLLECTION,'attempts':audit,'errors':errors,'counts':{k:len(v) for k,v in histories.items()},'quality_note':NOTE})
        if all(len(v)>=per_reservoir for v in histories.values()):break
    print('Final',json.dumps({k:len(v) for k,v in histories.items()}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=30);p.add_argument('--observations',type=int,default=2);a=p.parse_args();collect(a.limit,a.observations)
