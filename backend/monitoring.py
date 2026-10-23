"""Explainable monitoring, never drinking-water/toxicity certification."""
import json
from functools import lru_cache
from datetime import date
from backend.weather_quality import screen_weather
from backend.chlorophyll_review import review
from backend.config import DATA,MODEL,today,THRESHOLDS,CHL_THRESHOLDS,REGISTRY


def reservoirs():
    path=REGISTRY
    from backend.readiness import check
    return [r for r in json.loads(path.read_text()) if check(r)['ready']] if path.exists() else []

def model_status():
    path=MODEL/'metadata.json'
    files=[MODEL/'severity_mlp.pt',MODEL/'scaler.joblib',MODEL/'random_forest.joblib']
    if path.exists() and all(p.exists() for p in files):
        return json.loads(path.read_text())
    caml=DATA/'caml/audit.json'
    if caml.exists():
        audit=json.loads(caml.read_text())
        return {'status':'not_trained','training_source':'NASA SeaBASS CAML','label_records':audit['rows'],'reason':'CAML supplied severity labels parsed; genuine satellite alignment/training is in progress. Raw abundance units are unresolved.','missing_files':[],'metrics':None,'karnataka_field_validated':False,'forecast_horizon_days':None,'abundance_unit_audit':audit['abundance_audit']}
    return {'status':'not_trained','reason':'Genuine field labels and date/location-matched features are required before model training.','missing_files':[p.name for p in [DATA/'raw/train_labels.csv',DATA/'raw/metadata.csv'] if not p.exists()],'metrics':None,'karnataka_field_validated':False,'forecast_horizon_days':None}



@lru_cache(maxsize=2)
def load_models(version):
    import joblib,torch
    from pipeline.train import SeverityMLP
    checkpoint=torch.load(MODEL/'severity_mlp.pt',map_location='cpu',weights_only=True)
    model=SeverityMLP(checkpoint['n_inputs'],checkpoint['dropout']);model.load_state_dict(checkpoint['state_dict']);model.eval()
    return model,joblib.load(MODEL/'scaler.joblib'),joblib.load(MODEL/'random_forest.joblib')

def predict(observation):
    if model_status()['status']!='trained':return {'status':'unavailable','severity':None,'reason':'Genuine field-label severity training has not completed.','forecast_horizon_days':None}
    if observation is None or observation.get('status')!='available':return {'status':'unavailable','severity':None,'reason':'No quality-approved satellite features.'}
    import pandas as pd,torch
    from pipeline.features import FEATURE_NAMES
    version=tuple((MODEL/name).stat().st_mtime_ns for name in ['severity_mlp.pt','scaler.joblib','random_forest.joblib'])
    model,scaler,forest=load_models(version)
    values=pd.DataFrame([[observation['features'][f] for f in FEATURE_NAMES]],columns=FEATURE_NAMES)
    features=scaler.transform(values)
    with torch.no_grad():p=torch.softmax(model(torch.tensor(features,dtype=torch.float32)),dim=1)[0].numpy()
    baseline=int(forest.predict(features)[0])
    return {'status':'research_estimate','severity':int(p.argmax()+1),'random_forest_severity':baseline,'models_agree':int(p.argmax()+1)==baseline,'class_probability':float(p.max()),'confidence_note':'Uncalibrated model probability, not verified accuracy.','observed_at':observation['observed_at'],'forecast_horizon_days':0,'karnataka_field_validated':False,'numerical_density':None,'operational_use_supported':False,'reason':'Same-date research category estimate from CAML supplied labels. Raw abundance units remain unresolved; Karnataka field validation is not established.'}


def recommendation(latest,prediction,chl,change=None):
    recent_sat=bool(latest and 0<=(today()-date.fromisoformat(latest['observed_at'][:10])).days<=30)
    recent_chl=bool(chl and 0<=(today()-date.fromisoformat(chl['observed_at'][:10])).days<=30)
    if chl and change and change.get('absolute',0)>0:
        return {'status':'Monitor this lake','reason':f"Satellite chlorophyll estimates rose between {change['start']} and {change['end']}. This is a historical change flag; obtain a fresh observation and field sample. Product quality remains provisional where stated."}
    if not recent_sat and not recent_chl:
        return {'status':'Insufficient data','reason':'No quality-approved water-quality observation within the project’s 30-day freshness limit. Weather alone cannot establish bloom status.'}
    if recent_chl and chl.get('cyanobacteria_dominance_established'):
        value=chl['chlorophyll_a']
        if value>=50:return {'status':'Elevated monitoring priority','reason':'Recent chlorophyll exceeds the historical higher WHO guidance level and separately documented dominance is present. Field follow-up is recommended.'}
        if value>=10:return {'status':'Increased monitoring recommended','reason':'Recent chlorophyll meets the historical lower WHO guidance level with separately documented cyanobacteria dominance.'}
    if recent_chl and change and change.get('percent') is not None and change['absolute']>0:
        return {'status':'Increased monitoring recommended','reason':'Monitor this lake: comparable satellite chlorophyll estimates are rising. Confirm the change with a follow-up observation and field sampling; this does not establish toxicity.'}
    if recent_sat and prediction.get('operational_use_supported',False) and prediction.get('severity') is not None and prediction['severity']>=3:
        return {'status':'Increased monitoring recommended','reason':'An unvalidated Karnataka severity estimate suggests prioritizing field sampling; it does not establish toxicity.'}
    return {'status':'Routine monitoring','reason':'Continue collecting field and satellite observations. Available spectral indicators alone do not confirm a harmful bloom; chlorophyll guidance is inactive without dominance evidence.'}


def summary(identifier):
    record=next((r for r in reservoirs() if r['id']==identifier),None)
    if record is None:raise KeyError(identifier)
    path=DATA/'observations'/f'{identifier}.json'
    data=json.loads(path.read_text()) if path.exists() else {}
    observations=[o for o in data.get('observations',[]) if not o.get('observed_at') or o['observed_at'][:10]<=today().isoformat()]
    good=sorted({o['item_id']:o for o in observations if o.get('status')=='available'}.values(),key=lambda x:x['observed_at'])
    latest=good[-1] if good else None
    cp=DATA/'observations'/f'{identifier}-chlorophyll.json'
    chlorophyll=json.loads(cp.read_text()) if cp.exists() else []
    chlorophyll=sorted([o for o in chlorophyll if o['observed_at'][:10]<=today().isoformat()],key=lambda x:x['observed_at'])
    chl=chlorophyll[-1] if chlorophyll else None
    prediction=predict(latest)
    change=None
    if len(chlorophyll)>=2:
        prev,cur=chlorophyll[-2:]
        if prev['method']==cur['method'] and prev['source']==cur['source']:
            delta=cur['chlorophyll_a']-prev['chlorophyll_a']
            change={'absolute':delta,'percent':100*delta/prev['chlorophyll_a'] if prev['chlorophyll_a']>0 else None,'previous_concentration':prev['chlorophyll_a'],'current_concentration':cur['chlorophyll_a'],'start':prev['observed_at'],'end':cur['observed_at'],'basis':'Two observations from the same documented source and method'}
    months={}
    for o in observations:
        month=(o.get('query_end') or o.get('observed_at',''))[:7]
        if not month:continue
        m=months.setdefault(month,{'month':month,'acquisition_windows':0,'valid_observations':0,'missing_windows':0,'chlorophyll_values':[]})
        m['acquisition_windows']+=1;m['valid_observations']+=o.get('status')=='available';m['missing_windows']+=o.get('status')!='available'
    for o in chlorophyll:
        month=o['observed_at'][:7];m=months.setdefault(month,{'month':month,'acquisition_windows':0,'valid_observations':0,'missing_windows':0,'chlorophyll_values':[]});m['chlorophyll_values'].append(o['chlorophyll_a'])
    weather=data.get('weather',{})
    weather['rows']=[screen_weather(r) for r in weather.get('rows',[]) if r['date']<=today().isoformat()]
    for m in months.values():
        vals=m.pop('chlorophyll_values');m['chlorophyll_mean']=sum(vals)/len(vals) if vals else None;m['chlorophyll_count']=len(vals)
        rows=[r for r in weather['rows'] if r['date'].startswith(m['month'])]
        temps=[r['air_temperature_c'] for r in rows if r.get('air_temperature_c') is not None];rain=[r['rainfall_mm'] for r in rows if r.get('rainfall_mm') is not None]
        m['mean_air_temperature_c']=sum(temps)/len(temps) if temps else None;m['rainfall_mm']=sum(rain) if rain else None;m['weather_days']=len(rows);m['rainfall_days']=len(rain);m['excluded_rainfall_days']=sum('rainfall_mm_requires_source_review' in r.get('quality_flags',[]) for r in rows)
        if model_status()['status']=='trained':
            counts={str(i):0 for i in range(1,6)}
            for observation in good:
                if observation['observed_at'].startswith(m['month']):
                    estimate=predict(observation)
                    if estimate.get('severity'):counts[str(estimate['severity'])]+=1
            m['severity_distribution']=counts
        else:m['severity_distribution']=None
    return {'reservoir':record,'observations':observations,'latest':latest,'chlorophyll':chlorophyll,'latest_chlorophyll':chl,'change':change,'prediction':prediction,'review':review(chlorophyll),'recommendation':{'status':('Review '+review(chlorophyll)['status'].lower()),'reason':review(chlorophyll)['reason']},'weather':weather,'weather_error':data.get('weather_error'),'collection_errors':data.get('collection_errors',[]),'monthly':sorted(months.values(),key=lambda m:m['month'],reverse=True),'thresholds':THRESHOLDS,'chlorophyll_thresholds':CHL_THRESHOLDS,'model':model_status(),'updated_at':data.get('updated_at')}

# Preserve the original source data/API fields, but make the displayed values S2-only.
legacy_summary=summary
def summary(identifier):
    from backend.active import monitoring
    data=legacy_summary(identifier);active=monitoring(identifier)
    data['sentinel3_comparison']={'label':'Separate Sentinel-3 comparison source; not derived from displayed Sentinel-2 scene','latest':data['latest_chlorophyll'],'history':data['chlorophyll'],'change':data['change']}
    from backend.fai import observed
    data['fai']=observed(identifier)
    data.update(sentinel2=active,chlorophyll=active['history'],latest_chlorophyll=active['latest'] if active['chlorophyll_a'] is not None else None,change=active['change'],classification=active['classification'],trend=active['trend'])
    return data
