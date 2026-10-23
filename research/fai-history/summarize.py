"""Inventory actual outputs and construct fixed-horizon pairs without interpolation."""
from pathlib import Path
import json,pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data/fai-history';O=ROOT/'output/karnataka-fai-history';O.mkdir(exist_ok=True);registry=json.loads((ROOT/'data/reservoirs.json').read_text());allrows=[];counts=[];pairs=[]
for r in registry:
 p=D/r['id'];records=[]
 for f in p.glob('*.json'):
  x=json.loads(f.read_text())
  if 'status' in x:records.append(x)
 valid=sorted([x for x in records if x['status']=='valid'],key=lambda x:x['acquisition']);bydate={}
 for x in valid:
  day=x['acquisition'][:10]
  if day not in bydate or x['valid_fraction']>bydate[day]['valid_fraction']:bydate[day]=x
 valid=sorted(bydate.values(),key=lambda x:x['acquisition']);cat=json.loads((p/'catalogue-summary.json').read_text()) if (p/'catalogue-summary.json').exists() else {};gaps=[];n=0
 for i,x in enumerate(valid):
  t=pd.Timestamp(x['acquisition']);allrows.append({'reservoir_id':r['id'],'name':r['name'],'date':x['acquisition'],'scene_id':x['scene_id'],'fai':x['fai'],'valid_pixels':x['valid_pixels'],'valid_fraction':x['valid_fraction'],'source_urls':json.dumps(x['sources']),'metadata_file':str(next(f for f in p.glob('*.json') if f.stem==__import__('hashlib').sha256(x['scene_id'].encode()).hexdigest()[:20]))})
  if i:gaps.append((t-pd.Timestamp(valid[i-1]['acquisition'])).total_seconds()/86400)
  choices=[y for y in valid[i+1:] if 7<=(pd.Timestamp(y['acquisition'])-t).total_seconds()/86400<=13]
  if not choices:continue
  y=min(choices,key=lambda a:abs((pd.Timestamp(a['acquisition'])-t).total_seconds()/86400-10));n+=1
  pairs.append({'reservoir_id':r['id'],'issue_time':x['acquisition'],'target_time':y['acquisition'],'issue_scene':x['scene_id'],'target_scene':y['scene_id'],'fai_current':x['fai'],'target_fai':y['fai'],'lead_days':(pd.Timestamp(y['acquisition'])-t).total_seconds()/86400,'previous_fai':valid[i-1]['fai'] if i else None,'previous_age_days':gaps[-1] if i else None,'sin_doy':float(np.sin(2*np.pi*t.dayofyear/365.25)),'cos_doy':float(np.cos(2*np.pi*t.dayofyear/365.25))})
 counts.append({'reservoir_id':r['id'],'name':r['name'],'catalogue_complete':cat.get('complete',False),'catalogue_scenes':cat.get('raw_scenes',0),'acquisitions':cat.get('deduplicated_acquisitions',0),'processed':len(records),'valid_dates':len(valid),'target_pairs':n,'first_date':valid[0]['acquisition'] if valid else None,'last_date':valid[-1]['acquisition'] if valid else None,'median_gap_days':float(np.median(gaps)) if gaps else None,'max_gap_days':max(gaps) if gaps else None,'months':','.join(sorted({x['acquisition'][5:7] for x in valid})),'years':','.join(sorted({x['acquisition'][:4] for x in valid}))})
pd.DataFrame(counts).to_csv(O/'reservoir-counts.csv',index=False);pd.DataFrame(allrows).to_csv(O/'fai-time-series.csv',index=False);pd.DataFrame(pairs).to_csv(O/'forecast-pairs.csv',index=False)
s={'reservoirs':len(counts),'catalogues_complete':sum(x['catalogue_complete'] for x in counts),'planned_acquisitions':sum(x['acquisitions'] for x in counts),'processed':sum(x['processed'] for x in counts),'valid_dates':len(allrows),'pairs':len(pairs),'run_complete':all(x['catalogue_complete'] and x['processed']==x['acquisitions'] for x in counts)};(O/'progress.json').write_text(json.dumps(s,indent=2));print(s)
