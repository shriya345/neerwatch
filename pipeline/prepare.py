"""Acquire field-coordinate/date-matched Sentinel-2 features.
UID cache is resumable. No future observations, generated labels or target features.
Point samples use a 400 m area and conservative SCL water masking; this is
not a mapped reservoir-level statistic. Karnataka inference uses polygons.
"""
import argparse,json
import numpy as np
import pandas as pd
from shapely.geometry import box,mapping
from backend.config import DATA
from pipeline.train import read_labels
from pipeline.satellite import acquire

def prepare(limit=None):
    if (DATA/"caml/labels.csv").exists():raise ValueError("CAML source active: use python -m pipeline.caml_prepare for strictly preceding-date alignment and an explicit selection manifest.")
    labels=read_labels();cache=DATA/'cache/training';cache.mkdir(parents=True,exist_ok=True)
    for row in labels.iloc[:limit].itertuples():
        path=cache/f'{row.uid}.json'
        if path.exists():continue
        dy=400/111320;dx=dy/np.cos(np.deg2rad(row.latitude))
        geom=mapping(box(row.longitude-dx,row.latitude-dy,row.longitude+dx,row.latitude+dy))
        try:
            result,_,_=acquire(geom,row.date.date(),10)
            result.update(uid=row.uid,feature_latitude=row.latitude,feature_longitude=row.longitude,analysis_area='400 m field-site box; SCL water interior only')
        except Exception as e:result={'uid':row.uid,'status':'source_unavailable','reason':f'{type(e).__name__}: {str(e)[:150]}'}
        path.write_text(json.dumps(result,allow_nan=False));print(row.uid,result['status'],flush=True)
    rows=[];rejected=[]
    for row in labels.itertuples():
        p=cache/f'{row.uid}.json'
        if not p.exists():continue
        x=json.loads(p.read_text())
        if x['status']=='available':rows.append({k:x[k] for k in ['uid','observed_at','feature_latitude','feature_longitude','source_url']}|{'quality_status':x['status']}|x['features'])
        else:rejected.append({'uid':row.uid,'reason':x.get('reason')})
    if rows:pd.DataFrame(rows).to_csv(DATA/'training_features.csv',index=False)
    (DATA/'training_acquisition_summary.json').write_text(json.dumps({'matched_features':len(rows),'rejected':rejected,'total_field_labels':len(labels)},indent=2))
    print(f'{len(rows)} valid feature rows; {len(rejected)} rejected; {len(labels)} field labels.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);a=p.parse_args()
    try:prepare(a.limit)
    except ValueError as e:raise SystemExit(str(e))
