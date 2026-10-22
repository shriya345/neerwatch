"""Resumable genuine CAML/satellite matchups for a disclosed acquisition pilot.
No abundance conversion, fabricated labels, original competition split, or
missing-feature imputation. Samples are enriched by supplied severity category
for initial feasibility; test metrics describe this pilot, not population rates.
"""
import argparse,json,hashlib
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np,pandas as pd
from shapely.geometry import box,mapping
from backend.config import DATA,write_json
from pipeline.train import read_labels
from pipeline.satellite import acquire

def select_samples(per_class):
    frame=read_labels();audit=json.loads((DATA/'caml/audit.json').read_text())
    # This source-reported distance is a screening aid, not verified geolocation.
    eligible=frame[(frame.date>='2018-01-01')&frame.distance_to_water_m.notna()&(frame.distance_to_water_m<=100)]
    selection=pd.concat([g.sample(n=min(len(g),per_class),random_state=42) for _,g in eligible.groupby('severity')]).sort_values('uid')
    manifest={'source_sha256':audit['source_sha256'],'total_source_records':len(frame),'eligible_records':len(eligible),'selected_records':len(selection),'selection_rule':'2018+; source-reported distance to water <=100 m; seeded random selection capped per supplied class','per_class_cap':per_class,'eligible_class_counts':{str(int(k)):int(v) for k,v in eligible.severity.value_counts().sort_index().items()},'selected_class_counts':{str(int(k)):int(v) for k,v in selection.severity.value_counts().sort_index().items()},'seed':42,'uids':selection.uid.tolist(),'inference_scope':'Class-enriched, quality-selected acquisition pilot; metrics are not full-CAML population estimates or Karnataka validation.','satellite_alignment':'Strictly before sample calendar date, at most 10 days earlier. No original competition split is used.','spatial_support':'400 m radius field-coordinate box, valid SCL water interiors only. Does not establish the sampled parcel of water.'}
    write_json(DATA/'caml/acquisition_selection.json',manifest)
    return selection

def one(row,cache,retry_failed=False):
    path=cache/f'{row.uid}.json'
    if path.exists():
        cached=json.loads(path.read_text())
        if cached['status']=='available' or not retry_failed:return cached
    dy=400/111320;dx=dy/np.cos(np.deg2rad(row.latitude))
    geom=mapping(box(row.longitude-dx,row.latitude-dy,row.longitude+dx,row.latitude+dy))
    try:
        result,_,_=acquire(geom,row.date.date()-timedelta(days=1),lookback=9)
        result.update(uid=row.uid,feature_latitude=row.latitude,feature_longitude=row.longitude,sample_date=row.date.date().isoformat(),boundary_source='400 m radius box at original CAML coordinate; not a mapped waterbody polygon',label_basis='CAML supplied severity, independent of unresolved abun units',analysis_area='400 m radius box at original field sample coordinate; valid SCL water interiors')
    except Exception as e:result={'uid':row.uid,'status':'source_unavailable','reason':f'{type(e).__name__}: {str(e)[:180]}'}
    write_json(path,result);return result

def prepare(per_class=75,workers=4,retry_failed=False):
    selected=select_samples(per_class);cache=DATA/'cache/caml_training';cache.mkdir(parents=True,exist_ok=True)
    good=0;done=0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(one,row,cache,retry_failed) for row in selected.itertuples()]
        for future in as_completed(futures):
            r=future.result();done+=1;good+=r['status']=='available'
            if done%5==0 or done==len(futures):print(f'{done}/{len(futures)} completed; {good} quality-approved',flush=True)
    rows=[];rejected=[]
    for row in selected.itertuples():
        x=json.loads((cache/f'{row.uid}.json').read_text())
        if x['status']=='available':rows.append({k:x[k] for k in ['uid','observed_at','feature_latitude','feature_longitude','source_url']}|{'quality_status':'available'}|x['features'])
        else:rejected.append({'uid':row.uid,'status':x['status'],'reason':x.get('reason'),'attempts':x.get('attempts',[])})
    if rows:pd.DataFrame(rows).to_csv(DATA/'training_features.csv',index=False)
    write_json(DATA/'training_acquisition_summary.json',{'source':'NASA SeaBASS CAML','selected_records':len(selected),'matched_features':len(rows),'rejected':rejected,'class_counts_after_qc':{str(int(k)):int(v) for k,v in selected[selected.uid.isin([r['uid'] for r in rows])].severity.value_counts().sort_index().items()}})
    print(f'Finished: {len(rows)} genuine aligned feature rows.',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--per-class',type=int,default=75);p.add_argument('--workers',type=int,default=4);p.add_argument('--retry-failed',action='store_true');a=p.parse_args();prepare(a.per_class,a.workers,a.retry_failed)
