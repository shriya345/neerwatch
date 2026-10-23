from pathlib import Path
import json,hashlib,zipfile,os
import numpy as np,pandas as pd,lightgbm as lgb
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
r=json.loads((BASE/'results.json').read_text())
assert len(json.loads((ROOT/'data/reservoirs.json').read_text()))==46
assert hashlib.sha256((ROOT/'data/reservoirs.json').read_bytes()).hexdigest()==r['registry_sha256']
with zipfile.ZipFile(BASE.parent/'cyfi/cyfi/assets/model_v0.zip') as z:
 models=[lgb.Booster(model_str=z.read(n).decode()) for n in z.namelist() if n.startswith('lgb_model')]
checks=[]
for row in r['results']:
 if row['prediction_cells_per_ml'] is not None:
  f=pd.read_csv(BASE/f'{row["reservoir_id"]}-features.csv')[models[0].feature_name()]
  assert f.shape==(1,30) and np.isfinite(f.to_numpy()).all()
  d=float(np.round(np.expm1(max(0,np.mean([m.predict(f,num_threads=1)[0] for m in models])))))
  assert d==row['prediction_cells_per_ml']
  checks.append({'reservoir_id':row['reservoir_id'],'independently_rerun_from_saved_features':True,'density_cells_per_ml':d,'land_cover':int(f['land_cover'].iloc[0])})
 else:
  assert row['status']=='BLOCKED'
  checks.append({'reservoir_id':row['reservoir_id'],'no_prediction_when_qc_failed':True})
assert len(checks)==3
out={'inventory_unchanged':True,'all_46_preserved':True,'models_loaded':len(models),'tree_counts':[m.num_trees() for m in models],'checks':checks,'accuracy_evaluated':False,'production_approved':False}
(BASE/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
