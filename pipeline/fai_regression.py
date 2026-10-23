"""Offline future-FAI experiment. Consumes a frozen, provenance-bearing CSV only.
No dashboard inference is enabled by this module. CLI defaults to eligibility audit.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
FEATURES=['fai_current','fai_previous','previous_age_days','sin_doy','cos_doy']
def load(path,registry):
 d=pd.read_csv(path);required={'reservoir_id','date','fai','scene_id','source_urls','valid_pixels','valid_fraction'}
 if not required.issubset(d):raise ValueError('Missing provenance or quality columns')
 if not set(d.reservoir_id)<=set(registry):raise ValueError('Unknown reservoir')
 d['date']=pd.to_datetime(d.date,utc=True,errors='raise')
 if not np.isfinite(d[['fai','valid_pixels','valid_fraction']].to_numpy(dtype=float)).all():raise ValueError('Nonfinite observations')
 if (d.valid_pixels<25).any() or (d.valid_fraction<.1).any() or (d.valid_fraction>1).any():raise ValueError('Unapproved quality')
 if d[['scene_id','source_urls']].isna().any().any():raise ValueError('Missing provenance')
 if d.duplicated(['reservoir_id','date']).any():raise ValueError('Duplicate acquisition')
 return d.sort_values(['reservoir_id','date'])
def pairs(d):
 rows=[]
 for rid,g in d.groupby('reservoir_id'):
  g=g.sort_values('date').reset_index(drop=True)
  for i in range(1,len(g)):
   a=g.iloc[i];previous=g.iloc[i-1];gap=(a.date-previous.date).total_seconds()/86400
   if gap>30:continue
   candidates=g[(g.date>=a.date+pd.Timedelta(days=7))&(g.date<=a.date+pd.Timedelta(days=13))]
   if candidates.empty:continue
   b=candidates.iloc[np.argmin(abs((candidates.date-a.date).dt.total_seconds()/86400-10).to_numpy())]
   rows.append(dict(reservoir_id=rid,issue_time=a.date,target_time=b.date,issue_scene=a.scene_id,target_scene=b.scene_id,target=float(b.fai),fai_current=float(a.fai),fai_previous=float(previous.fai),previous_age_days=gap,sin_doy=np.sin(2*np.pi*a.date.dayofyear/365.25),cos_doy=np.cos(2*np.pi*a.date.dayofyear/365.25)))
 return pd.DataFrame(rows)
def split(p):
 if p.empty:return {k:p.copy() for k in ['train','validation','test']}
 # Entire potential target window must precede boundary; all reservoirs share cutoffs.
 v=pd.Timestamp('2025-01-01',tz='UTC');t=pd.Timestamp('2026-01-01',tz='UTC')
 out={'train':p[(p.issue_time+pd.Timedelta(days=13)<v)&(p.target_time<v)],'validation':p[(p.issue_time>=v)&(p.issue_time+pd.Timedelta(days=13)<t)&(p.target_time<t)],'test':p[p.issue_time>=t]}
 # Each future reservoir observation is one target per split.
 out={k:x.sort_values('issue_time').drop_duplicates(['reservoir_id','target_time'],keep='last') for k,x in out.items()}
 for a,b in [('train','validation'),('train','test'),('validation','test')]:
  if set(out[a].target_scene)&set(out[b].target_scene):raise ValueError('Shared target scene across partitions')
 return out
def eligibility(d,parts):
 reasons=[]
 if not set(range(2022,2027))<=set(d.date.dt.year):reasons.append('All five years 2022–2026 required')
 for name,minimum in [('train',300),('validation',100),('test',100)]:
  x=parts[name]
  if len(x)<minimum:reasons.append(f'{name}: fewer than {minimum} independent targets')
  if x.empty or x.reservoir_id.nunique()<20:reasons.append(f'{name}: fewer than 20 reservoirs')
  if x.empty or x.target_time.dt.quarter.nunique()<4:reasons.append(f'{name}: incomplete seasonal coverage')
 return {'eligible':not reasons,'reasons':reasons,'counts':{k:len(v) for k,v in parts.items()},'note':'Conservative experiment gates, not a guarantee of scientific validity'}
def metrics(y,p):
 from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
 return {'MAE':float(mean_absolute_error(y,p)),'RMSE':float(mean_squared_error(y,p)**.5),'R2':float(r2_score(y,p)) if len(y)>1 and np.var(y)>0 else None,'n':len(y)}
def run(path,output,train=False):
 from backend.config import DATA
 registry=[r['id'] for r in json.loads((DATA/'reservoirs.json').read_text())];d=load(path,registry);p=pairs(d);parts=split(p);gate=eligibility(d,parts)
 if not train:return gate
 if not gate['eligible']:raise ValueError('Training refused: '+'; '.join(gate['reasons']))
 from sklearn.ensemble import RandomForestRegressor
 import joblib
 output=Path(output)
 if output.exists():raise ValueError('Use a new model output directory')
 # No tuning on test; fixed configuration defined before any evaluation.
 config=dict(n_estimators=500,max_depth=12,min_samples_leaf=10,max_features=1.0,random_state=42,n_jobs=-1)
 model=RandomForestRegressor(**config);model.fit(parts['train'][FEATURES],parts['train'].target)
 result={};predictions=[]
 for name in ['validation','test']:
  x=parts[name].copy();x['prediction']=model.predict(x[FEATURES]);result[name]={'model':metrics(x.target,x.prediction),'persistence':metrics(x.target,x.fai_current),'by_reservoir':{},'by_season':{}}
  for rid,g in x.groupby('reservoir_id'):result[name]['by_reservoir'][rid]={'model':metrics(g.target,g.prediction),'persistence':metrics(g.target,g.fai_current)}
  month=x.target_time.dt.month;x['season']=np.select([month<=2,month<=5,month<=9],['winter','pre-monsoon','southwest-monsoon'],default='post-monsoon')
  for season,g in x.groupby('season'):result[name]['by_season'][season]={'model':metrics(g.target,g.prediction),'persistence':metrics(g.target,g.fai_current)}
  x['partition']=name;predictions.append(x)
 output.mkdir(parents=True);joblib.dump(model,output/'random_forest.joblib');pd.concat(predictions).to_csv(output/'heldout_predictions.csv',index=False)
 for name,x in parts.items():x.to_csv(output/f'{name}_pairs.csv',index=False)
 metadata={'configuration':config,'features':FEATURES,'horizon_days':10,'tolerance_days':[7,13],'dataset_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'eligibility':gate,'metrics':result,'deployed':False,'target':'future observed dimensionless FAI; not measured biomass','supported_reservoirs':sorted(parts['train'].reservoir_id.unique()),'baseline':'persistence','versions':{'sklearn':__import__('sklearn').__version__,'numpy':np.__version__}}
 (output/'metadata.json').write_text(json.dumps(metadata,indent=2,allow_nan=False));return metadata
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('snapshot');parser.add_argument('--output',default='models/fai-experiment');parser.add_argument('--train',action='store_true');args=parser.parse_args();print(json.dumps(run(args.snapshot,args.output,args.train),indent=2))
