"""Import authorized original provider rasters, never old application outputs.
Source QFLAG is retained without guessed bit meanings. Published values are
provisional product estimates, not field observations or forecasting targets.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from datetime import date,timedelta
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from scipy.ndimage import binary_erosion
from backend.config import DATA,write_json,today
from backend.monitoring import reservoirs
from pipeline.clms import SOURCE

METHOD='CLMS OLCI 300 m: median provider CHLAMEAN of finite interior pixels; provisional quality review'
NOTE='Provisional Copernicus satellite estimate (10-day composite), not a field measurement. Interior water mask, dataMask, NOBS and finite-value screening applied. Provider quality flags and relative uncertainty are retained; full flag interpretation and local accuracy remain unverified.'
def run(directory):
    directory=Path(directory);cache=DATA/'satellite-originals/clms';cache.mkdir(parents=True,exist_ok=True)
    records=reservoirs();out={r['id']:[] for r in records};audit=[]
    for path in sorted(directory.glob('*.tif')):
        side=path.with_suffix('.json')
        if not side.exists():continue
        meta=json.loads(side.read_text());digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=meta.get('sha256'):raise ValueError(f'Hash mismatch: {path.name}')
        bands=meta.get('bands',[])
        if not {'CHLAMEAN','CHLAUNC','QFLAG','NOBS','dataMask'}.issubset(bands):raise ValueError(f'Unknown bands {path.name}')
        if meta.get('collection')!='byoc-5c2c9b2c-2893-41d9-b2bc-fbd6e5b8b31d':raise ValueError('Unexpected source collection')
        end=date.fromisoformat(meta['period_end'][:10]);start=meta['period_start'][:10]
        if end>=today():continue
        with rasterio.open(path) as src:
            if src.count!=len(bands):raise ValueError('Band count mismatch')
            values={b:src.read(i+1) for i,b in enumerate(bands)}
            for record in records:
                geom=json.loads((DATA/'boundaries'/f"{record['id']}.geojson").read_text())['geometry']
                geom=transform_geom('EPSG:4326',src.crs,geom)
                interior=geometry_mask([geom],out_shape=src.shape,transform=src.transform,invert=True)
                # Exclude one native cell at the shoreline; never include raster edges.
                interior=binary_erosion(interior,iterations=1)
                total=int(interior.sum())
                if total<3:continue
                chl=values['CHLAMEAN'];unc=values['CHLAUNC'];q=values['QFLAG']
                valid=interior&(values['dataMask']==1)&(values['NOBS']>=1)&np.isfinite(chl)&(chl>0)&(chl<10000)&np.isfinite(unc)&(unc>=0)&(unc<1e30)&(q!=65535)
                n=int(valid.sum());coverage=n/total
                if n<3 or coverage<.1:continue
                flags,counts=np.unique(q[valid],return_counts=True)
                row={'reservoir_id':record['id'],'observed_at':str(end),'period_start':start,'period_end_exclusive':str(end+timedelta(days=1)),'chlorophyll_a':float(np.median(chl[valid])),'unit':'µg/L','source':'Copernicus CLMS LWQ NRT OLCI v2 300 m 10-daily','source_url':SOURCE,'method':METHOD,'quality_status':'provisional_provider_estimate','quality_note':NOTE,'cyanobacteria_dominance_established':False,'relative_uncertainty_percent':float(np.median(unc[valid])),'quality':{'valid_pixels':n,'interior_pixels':total,'valid_fraction':coverage,'qflag_histogram':{str(int(k)):int(v) for k,v in zip(flags,counts)},'screening':'Project spatial/finite-value screening only; provider QFLAG meaning not asserted'},'source_raster':path.name,'source_sha256':digest,'source_product':meta['candidate_product'],'retrieved_at':meta['retrieved_at'],'publication_time_verified':False,'forecast_training_eligible':False}
                out[record['id']].append(row)
        shutil.copy2(path,cache/path.name);shutil.copy2(side,cache/side.name)
        audit.append({'file':path.name,'sha256':digest,'hash_verified':True,'bands':bands})
    for identifier,rows in out.items():
        dedup={r['period_start']:r for r in rows}
        write_json(DATA/'observations'/f'{identifier}-chlorophyll.json',sorted(dedup.values(),key=lambda r:r['observed_at']))
    write_json(DATA/'clms-archive-audit.json',{'source_directory':str(directory),'original_rasters':audit,'counts':{k:len({r['period_start'] for r in v}) for k,v in out.items()},'quality_note':NOTE,'unit_reference':SOURCE,'unit_equivalence':'1 mg/m³ = 1 µg/L; CLMS CHLAMEAN is concentration, not raw reflectance','forecast_training_eligible':False})
    print(json.dumps({k:len(v) for k,v in out.items()}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');run(p.parse_args().directory)
