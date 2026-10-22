"""Sentinel-2 L2A retrieval: no credentials, signed Planetary Computer COGs.
Upstream methodology: historical STAC search + multiband summary features.
"""
import json, math, time, threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
import httpx
import numpy as np
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from rasterio.warp import transform_geom
from shapely.geometry import shape, mapping
from backend.config import DATA
from pipeline.features import BANDS, extract_features
TOKEN_CACHE={}
TOKEN_LOCK=threading.Lock()
class InsufficientWaterError(ValueError):
    def __init__(self,message,quality=None):
        super().__init__(message);self.quality=quality or {}
STAC='https://planetarycomputer.microsoft.com/api/stac/v1/search'


def search(geometry, day, lookback=10, limit=30):
    """Follow STAC pagination; the window applies to every returned scene."""
    day=date.fromisoformat(str(day)[:10])
    bbox=list(shape(geometry).bounds)
    params={'collections':'sentinel-2-l2a','bbox':','.join(map(str,bbox)),'datetime':f'{day-timedelta(days=lookback)}T00:00:00Z/{day}T23:59:59Z','limit':limit,'sortby':'-properties.datetime'}
    items=[];seen=set();url=STAC
    with httpx.Client(timeout=45,follow_redirects=True) as c:
        while url:
            r=c.get(url,params=params);r.raise_for_status();page=r.json()
            for item in page['features']:
                if item['id'] not in seen:items.append(item);seen.add(item['id'])
            link=next((x for x in page.get('links',[]) if x.get('rel')=='next'),None)
            url=link['href'] if link else None;params=None
    return [x for x in items if day-timedelta(days=lookback)<=date.fromisoformat(x['properties']['datetime'][:10])<=day]


def read_item(item, geometry, resolution=60, progress=None):
    import pyproj
    centroid=shape(geometry).centroid
    epsg=32600+int((centroid.x+180)//6)+1
    crs=f'EPSG:{epsg}'
    projected=shape(transform_geom('EPSG:4326',crs,geometry))
    left,bottom,right,top=projected.bounds
    width=math.ceil((right-left)/resolution);height=math.ceil((top-bottom)/resolution)
    if width*height>1_500_000:
        raise ValueError('Analysis area exceeds the 60 m screening grid limit; split the reservoir into tiles.')
    transform=from_origin(left,top,resolution,resolution)
    mask=geometry_mask([mapping(projected)],out_shape=(height,width),transform=transform,invert=True)
    tiles=item.get('_mosaic_items',[item])
    if len(tiles)>1:
        dates={t['properties']['datetime'][:10] for t in tiles}
        times=[datetime.fromisoformat(t['properties']['datetime'].replace('Z','+00:00')) for t in tiles]
        keys={(t['properties'].get('platform'),t['properties'].get('sat:relative_orbit'),t['properties'].get('s2:processing_baseline')) for t in tiles}
        if len(dates)!=1 or len(keys)!=1 or (max(times)-min(times)).total_seconds()>300:raise ValueError('Mosaic acquisitions must share date, platform, relative orbit and baseline, within 300 seconds')
    arrays={};scl=None;band_metadata={};owner=np.full((height,width),-1,dtype='int16')
    with httpx.Client(timeout=40,follow_redirects=True) as client, rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='35',GDAL_HTTP_MAX_RETRY='1'):
        for b in ['SCL']+BANDS:
            if progress:progress(b)
            merged=np.zeros((height,width),dtype='uint8') if b=='SCL' else np.full((height,width),np.nan,dtype='float32')
            metadata=[]
            for ti,tile in enumerate(tiles):
                asset=tile['assets'][b]
                parsed=urlparse(asset['href']);account=parsed.netloc.split('.')[0];container=parsed.path.split('/')[1];key=(account,container)
                with TOKEN_LOCK:
                    if key not in TOKEN_CACHE or TOKEN_CACHE[key][0]<time.time():
                        response=client.get(f'https://planetarycomputer.microsoft.com/api/sas/v1/token/{account}/{container}');response.raise_for_status()
                        TOKEN_CACHE[key]=(time.time()+1800,response.json()['token'])
                href=asset['href']+'?'+TOKEN_CACHE[key][1]
                with rasterio.open(href) as src:
                    with WarpedVRT(src,crs=crs,transform=transform,width=width,height=height,resampling=Resampling.nearest,nodata=0) as vrt:raw=vrt.read(1)
                    if b=='SCL':
                        take=(owner<0)&(raw>0);owner[take]=ti;merged[take]=raw[take]
                    else:
                        rb=asset.get('raster:bands',[{}])[0];baseline=float(tile['properties'].get('s2:processing_baseline','0'))
                        scale=rb.get('scale',.0001);offset=rb.get('offset',-.1 if baseline>=4 else 0)
                        arr=raw.astype('float32')*scale+offset;arr[raw==0]=np.nan;take=owner==ti;merged[take]=arr[take]
                        metadata.append({'scene_id':tile['id'],'scale':scale,'offset':offset,'processing_baseline':baseline,'native_crs':str(src.crs),'native_resolution_m':list(src.res),'source_href':asset['href'],'analysis_crs':crs,'analysis_resolution_m':resolution})
            if b=='SCL':
                from scipy.ndimage import binary_erosion,binary_dilation
                scl=merged
                grid_coverage=float(((owner>=0)&mask).sum()/max(1,mask.sum()))
                if len(tiles)>1 and grid_coverage<.95:raise InsufficientWaterError(f'Mosaic data footprint only {grid_coverage:.1%}; requires 95% of reservoir',{'mosaic_grid_coverage':grid_coverage})
                candidate=binary_erosion(mask&(scl==6),iterations=max(1,int(np.ceil(60/resolution))))&~binary_dilation(np.isin(scl,[3,8,9,10]),iterations=max(1,int(np.ceil(60/resolution))))
                if candidate.sum()<25 or candidate.sum()/max(1,mask.sum())<.10:raise InsufficientWaterError(f'Only {int(candidate.sum())} cloud-free interior water pixels in {int(mask.sum())} polygon pixels; fails unchanged minimum count/coverage gates.',{'valid_pixels':int(candidate.sum()),'polygon_pixels':int(mask.sum()),'valid_fraction':float(candidate.sum()/max(1,mask.sum()))})
            else:arrays[b]=merged;band_metadata[b]=metadata[0] if len(tiles)==1 else {'tiles':metadata,'analysis_crs':crs,'analysis_resolution_m':resolution}
    result=extract_features(arrays,scl,mask,resolution)
    from scipy.ndimage import binary_erosion,binary_dilation
    valid=binary_erosion(mask&(scl==6),iterations=max(1,int(np.ceil(60/resolution))))&~binary_dilation(np.isin(scl,[3,8,9,10]),iterations=max(1,int(np.ceil(60/resolution))))
    for array in arrays.values():valid &= np.isfinite(array)&(array>0)&(array<=1)
    arrays['_valid_water_mask']=valid
    arrays['_scl']=scl
    if len(tiles)>1:arrays['_tile_index']=owner
    result['quality']['data_footprint_fraction']=grid_coverage
    result['quality']['mosaic_tile_count']=len(tiles)
    result['quality']['scl_water_pixels']=int((mask&(scl==6)).sum())
    result['quality']['interior_cloud_free_pixels']=int(candidate.sum())
    result['spectral_bands']=band_metadata
    result.update(item_id=item['id'],observed_at=item['properties']['datetime'],source='Copernicus Sentinel-2 L2A / Microsoft Planetary Computer',source_url=f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/{tiles[0]['id']}",retrieved_at=datetime.now(timezone.utc).isoformat(),boundary_source='Caller-supplied analysis geometry; boundary provenance must be supplied by the caller',cyanobacteria_dominance_established=False,chlorophyll_a=None,chlorophyll_note='No calibrated chlorophyll-a concentration is available from this Sentinel-2 extraction. NDCI is a spectral index, not a concentration.')
    return result,arrays,mask


def acquire(geometry, day, lookback=10):
    items=search(geometry,day,lookback)
    # Favor low scene cloud cover, retaining the latest viable imagery.
    area=shape(geometry)
    items.sort(key=lambda x:(-round(shape(x['geometry']).intersection(area).area/area.area,1),float(x['properties'].get('eo:cloud_cover',100)), -datetime.fromisoformat(x['properties']['datetime'].replace('Z','+00:00')).timestamp()))
    failures=[]
    for item in items[:3]:
        try:
            result,arrays,mask=read_item(item,geometry)
            if result['status']=='available':return result,arrays,mask
            failures.append(result)
        except Exception as exc:failures.append({'item_id':item['id'],'status':'insufficient_data' if isinstance(exc,InsufficientWaterError) else 'source_unavailable','reason':f'{type(exc).__name__}: {str(exc)[:180]}'})
    return {'status':'insufficient_data','features':None,'reason':'No usable satellite observation in the historical lookback window.','attempts':failures,'observed_at':None,'chlorophyll_a':None},None,None


def save_rgb(arrays, mask, path):
    from PIL import Image
    # Fixed display stretch only; not used for measurements/model input.
    rgb=np.stack([arrays[b] for b in ['B04','B03','B02']],axis=-1)
    rgb=np.nan_to_num(np.clip(rgb/.25,0,1))
    Image.fromarray((rgb*255).astype('uint8')).save(path)
