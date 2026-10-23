from pathlib import Path
import json,csv,zipfile,re
BASE=Path(__file__).resolve().parent
out=[]
with zipfile.ZipFile(BASE.parent/'cyfi/cyfi/assets/model_v0.zip') as z:
 for rid in ['krs','bhadra']:
  row=next(csv.DictReader(open(BASE/f'{rid}-features.csv')))
  for name in [n for n in z.namelist() if n.startswith('lgb_model')]:
   lines=z.read(name).decode().splitlines()
   features=next(x for x in lines if x.startswith('feature_names=')).split('=',1)[1].split()
   ranges=next(x for x in lines if x.startswith('feature_infos=')).split('=',1)[1].split()
   bad=[]
   for f,r in zip(features,ranges):
    if f not in row: continue
    m=re.fullmatch(r'\[([^:]+):([^\]]+)\]',r)
    if not m: continue
    lo,hi=map(float,m.groups());v=float(row[f])
    if v<lo or v>hi:bad.append(dict(feature=f,value=v,min=lo,max=hi))
   out.append(dict(reservoir_id=rid,model=name,out_of_training_range=bad))
(BASE/'feature-range-check.json').write_text(json.dumps(out,indent=2))
print([(r['reservoir_id'],r['model'],len(r['out_of_training_range'])) for r in out])
