"""Read-only acquisition monitor. Does not restart or alter the running queue."""
import json,hashlib
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[2];D=R/'data/fai-history';O=R/'output/karnataka-fai-history';registry=json.loads((R/'data/reservoirs.json').read_text());manifest=json.loads((D/'manifest.json').read_text());assert manifest['registry_sha256']==hashlib.sha256((R/'data/reservoirs.json').read_bytes()).hexdigest()
rows=[];pair_count=0
def season(month):return 'winter' if month<=2 else 'pre-monsoon' if month<=5 else 'southwest-monsoon' if month<=9 else 'post-monsoon'
for r in registry:
 p=D/r['id'];planned={};results=[]
 for f in (p/'catalogue').glob('*.json'):
  q=json.loads(f.read_text())
  for x in q.get('features',[]):
   a=x['properties'];key=(a['datetime'][:10],a.get('platform'),a.get('sat:relative_orbit'));planned[key]=a['datetime'][:7]
 for f in p.glob('*.json'):
  try:q=json.loads(f.read_text())
  except json.JSONDecodeError:continue
  if 'status' in q:results.append(q)
 dates=sorted({x['acquisition'] for x in results if x['status']=='valid'})
 for i,t in enumerate(dates):
  if any(7<=(pd.Timestamp(y)-pd.Timestamp(t)).total_seconds()/86400<=13 for y in dates[i+1:]):pair_count+=1
 for month in sorted(set(planned.values())):
  got=[x for x in results if x['acquisition'].startswith(month)];valid=[x for x in got if x['status']=='valid'];quality=[x for x in got if x.get('reason','').startswith(('InsufficientWaterError:','ValueError:'))];total=sum(m==month for m in planned.values())
  rows.append(dict(reservoir_id=r['id'],name=r['name'],year=int(month[:4]),month=month,season=season(int(month[5:])),planned_acquisitions=total,processed_acquisitions=len(got),valid_acquisitions=len(valid),valid_dates=len({x['acquisition'][:10] for x in valid}),quality_rejections=len(quality),retryable_errors=len(got)-len(valid)-len(quality),unprocessed=max(0,total-len(got))))
d=pd.DataFrame(rows);d.to_csv(O/'progress-by-reservoir-year-month.csv',index=False);numeric=['planned_acquisitions','processed_acquisitions','valid_acquisitions','valid_dates','quality_rejections','retryable_errors','unprocessed']
for keys,name in [(['year'],'progress-by-year.csv'),(['year','season'],'progress-by-year-season.csv'),(['month'],'progress-by-month.csv')]:d.groupby(keys)[numeric].sum().to_csv(O/name)
progress=json.loads((O/'progress.json').read_text());years=sorted(d[d.valid_dates>0].year.unique().tolist());seasons=sorted(d[d.valid_dates>0].season.unique().tolist());summary={'snapshot_utc':pd.Timestamp.now(tz='UTC').isoformat(),'years_with_valid_observations':years,'seasons_with_valid_observations':seasons,'five_year_gate_passes':set(years)==set(range(2022,2027)),'totals':{k:int(d[k].sum()) for k in numeric},'forecast_pairs':pair_count,'scope':'Exactly current 46 registry records; cutoff remains 2026-10-22','ml_status':'NOT EVALUATED: full year/season and chronological sample gates required'};(O/'coverage-checkpoint.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
