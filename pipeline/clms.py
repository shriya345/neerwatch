"""Credential-gated Copernicus CLMS chlorophyll collection and QC review.
Raw arrays are retained; concentrations are NOT published before documented
provider QFLAG selection is configured. Never treats FCBPROB as field dominance.
"""
import argparse,json,os,math
from io import BytesIO
from datetime import date,timedelta,datetime,timezone
import httpx,numpy as np,rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from shapely.geometry import shape,mapping
from scipy.ndimage import binary_erosion
from backend.config import DATA,today
from backend.monitoring import reservoirs
COLLECTION='5c2c9b2c-2893-41d9-b2bc-fbd6e5b8b31d'
SOURCE='https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/clms/bio-geophysical-parameters/water-bodies/lake-water-quality/lwq-nrt_global_300m_10daily_v2.html'
BANDS=['CHLAMEAN','CHLAUNC','FCBPROB','QFLAG','NOBS','dataMask']
EVALSCRIPT='''//VERSION=3
function setup(){return {input:[{bands:["CHLAMEAN","CHLAUNC","FCBPROB","QFLAG","NOBS","dataMask"]}],output:{bands:6,sampleType:"FLOAT32"}}}
function evaluatePixel(s){return [s.CHLAMEAN,s.CHLAUNC,s.FCBPROB,s.QFLAG,s.NOBS,s.dataMask]}
'''

def token(client):
    client_id=os.environ.get('CDSE_CLIENT_ID');secret=os.environ.get('CDSE_CLIENT_SECRET')
    if not client_id or not secret:
        raise ValueError('Set CDSE_CLIENT_ID and CDSE_CLIENT_SECRET from a Copernicus Data Space Sentinel Hub OAuth client. See docs/DATA_SETUP.md. Credentials stay on the backend.')
    r=client.post('https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',data={'grant_type':'client_credentials','client_id':client_id,'client_secret':secret});r.raise_for_status();return r.json()['access_token']

def retrieve(identifier,period):
    record=next((r for r in reservoirs() if r['id']==identifier),None)
    if not record:raise ValueError('Unknown reservoir.')
    start=date.fromisoformat(period)
    if start.day not in [1,11,21]:raise ValueError('Select a nominal 10-day composite start (day 1, 11 or 21).')
    end=(start+timedelta(days=10)) if start.day!=21 else (start.replace(day=28)+timedelta(days=4)).replace(day=1)
    if end>today():raise ValueError('Composite is not complete; future information is excluded.')
    boundary=DATA/'boundaries'/f'{identifier}.geojson'
    if not boundary.exists():raise ValueError('Mapped polygon required.')
    geom=json.loads(boundary.read_text())['geometry'];centre=shape(geom).centroid;crs=32600+int((centre.x+180)//6)+1
    projected=shape(transform_geom('EPSG:4326',f'EPSG:{crs}',geom));bbox=list(projected.bounds)
    width=max(1,math.ceil((bbox[2]-bbox[0])/300));height=max(1,math.ceil((bbox[3]-bbox[1])/300))
    payload={'input':{'bounds':{'bbox':bbox,'properties':{'crs':f'http://www.opengis.net/def/crs/EPSG/0/{crs}'}},'data':[{'type':'byoc-'+COLLECTION,'dataFilter':{'timeRange':{'from':start.isoformat()+'T00:00:00Z','to':start.isoformat()+'T23:59:59Z'}},'processing':{'upsampling':'NEAREST','downsampling':'NEAREST'}}]},'output':{'width':width,'height':height,'responses':[{'identifier':'default','format':{'type':'image/tiff'}}]},'evalscript':EVALSCRIPT}
    cache=DATA/'cache/clms';cache.mkdir(parents=True,exist_ok=True)
    with httpx.Client(timeout=120,follow_redirects=True) as client:
        access=token(client)
        response=client.post('https://sh.dataspace.copernicus.eu/api/v1/process',json=payload,headers={'Authorization':'Bearer '+access});response.raise_for_status()
    target=cache/f'{identifier}-{start}.tif';target.write_bytes(response.content)
    with rasterio.io.MemoryFile(response.content) as mem:
        with mem.open() as src:
            values=src.read();mask=geometry_mask([mapping(projected)],out_shape=(src.height,src.width),transform=src.transform,invert=True)
            mask=binary_erosion(mask,iterations=1) # At least one ~300 m shoreline cell.
    if values.shape[0]!=6:raise ValueError('Unexpected CLMS band count.')
    chl,unc,fcb,qflag,nobs,data_mask=values
    raw_valid=mask&(data_mask==1)&np.isfinite(chl)&(chl>=0)&(chl<=10000)&(nobs>=1)
    unique,counts=np.unique(qflag[raw_valid],return_counts=True)
    metadata={'reservoir_id':identifier,'source':'Copernicus CLMS Lake Water Quality NRT v2, 300 m, 10-day composite','source_url':SOURCE,'nominal_period_start':str(start),'period_end_exclusive':str(end),'retrieved_at':datetime.now(timezone.utc).isoformat(),'candidate_water_pixels':int(raw_valid.sum()),'qflag_histogram':{str(int(k)):int(v) for k,v in zip(unique,counts)},'quality_status':'pending_provider_flag_review','note':'Raw retrieval is not an approved concentration; no field dominance inference from FCBPROB. Availability/publication time must be checked for forecasting.'}
    policy_path=DATA/'clms-quality-policy.json'
    if policy_path.exists():
        policy=json.loads(policy_path.read_text())
        required={'accepted_qflags','provider_manual_url','max_relative_uncertainty_percent','min_pixels','min_coverage'}
        if not required.issubset(policy) or not policy['provider_manual_url'].startswith('https://land.copernicus.eu/'):
            raise ValueError('QC policy requires exact provider manual provenance and explicit acceptance values.')
        valid=raw_valid&np.isin(qflag,policy['accepted_qflags'])&np.isfinite(unc)&(unc>=0)&(unc<=policy['max_relative_uncertainty_percent'])
        coverage=float(valid.sum()/mask.sum()) if mask.sum() else 0
        metadata.update(valid_pixels=int(valid.sum()),valid_fraction=coverage,quality_policy=policy)
        if valid.sum()>=policy['min_pixels'] and coverage>=policy['min_coverage']:
            row={'reservoir_id':identifier,'observed_at':(end-timedelta(days=1)).isoformat(),'period_start':str(start),'period_end_exclusive':str(end),'chlorophyll_a':float(np.median(chl[valid])),'unit':'µg/L','source':metadata['source'],'source_url':SOURCE,'method':'CLMS provider chlorophyll-a estimate; median of QC-screened reservoir interior pixels','quality_status':'approved','cyanobacteria_dominance_established':False,'relative_uncertainty_percent':float(np.median(unc[valid])),'quality':metadata,'publication_time_verified':False}
            destination=DATA/'observations'/f'{identifier}-chlorophyll.json';rows=json.loads(destination.read_text()) if destination.exists() else []
            rows=[r for r in rows if r.get('period_start')!=str(start)];rows.append(row);destination.write_text(json.dumps(rows,indent=2,allow_nan=False));metadata['quality_status']='approved'
        else:metadata['quality_status']='insufficient_data'
    target.with_suffix('.json').write_text(json.dumps(metadata,indent=2,allow_nan=False))
    print(json.dumps(metadata,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reservoir',required=True);p.add_argument('--period-start',required=True);a=p.parse_args()
    try:retrieve(a.reservoir,a.period_start)
    except ValueError as e:raise SystemExit(str(e))
