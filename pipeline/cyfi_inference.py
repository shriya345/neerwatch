"""Research-only inference over frozen original CyFi band crops. No network or training."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def infer(identifier):
 import numpy as np,pandas as pd,lightgbm as lgb,yaml
 from cyfi.config import FeaturesConfig
 from cyfi.data.features import _calculate_satellite_features_for_sample_item
 from cyfi import config as config_module
 from cyfi.data import features as feature_module
 snapshot=json.loads((ROOT/'data/cyfi/inputs-v1.json').read_text())
 if identifier not in {r['id'] for r in json.loads((ROOT/'data/reservoirs.json').read_text())}:raise ValueError('Unknown reservoir')
 if digest(ROOT/'data/reservoirs.json')!=snapshot['registry_sha256']:raise ValueError('Reservoir registry differs from reviewed snapshot')
 from importlib.metadata import version
 for package,expected in snapshot['runtime_versions'].items():
  if version(package)!=expected:raise ValueError(f'CyFi runtime version mismatch: {package}')
 row=snapshot['records'][identifier]
 if row['status']!='eligible':raise ValueError(row['reason'])
 if row['cloud_fraction']>.05 or row['inside_fraction']<.95:raise ValueError('Spatial or cloud quality screening failed')
 for module,key in [(config_module,'config.py'),(feature_module,'data/features.py')]:
  if digest(Path(module.__file__))!=snapshot['upstream_source_sha256'][key]:raise ValueError('CyFi preprocessing source differs from reviewed version')
 model=ROOT/'models/cyfi/model_v0.zip'
 if digest(model)!=snapshot['model_sha256']:raise ValueError('Original model checksum mismatch')
 for band,info in row['band_files'].items():
  path=ROOT/row['cache_base']/f'sentinel_2000/{identifier}/{row["scene_id"]}/{band}.npy'
  if not path.exists():raise ValueError(f'Missing original satellite band: {band}')
  if digest(path)!=info['sha256']:raise ValueError(f'Original satellite band checksum mismatch: {band}')
 with zipfile.ZipFile(model) as z:
  cfg=FeaturesConfig(**yaml.safe_load(z.read('features_config.yaml')))
  names=sorted(n for n in z.namelist() if n.startswith('lgb_model_'))
  if len(names)!=5:raise ValueError('Expected five original regressors')
  models=[lgb.Booster(model_str=z.read(n).decode()) for n in names]
 if set(row['band_files'])!=set(cfg.use_sentinel_bands):raise ValueError('Incomplete band provenance')
 f=_calculate_satellite_features_for_sample_item(identifier,row['scene_id'],cfg,ROOT/row['cache_base'])
 if not all(k in f and np.isfinite(f[k]) for k in cfg.satellite_image_features):raise ValueError('Upstream spectral quality screening failed')
 f.update(month=int(row['acquisition_date'][5:7]),days_before_sample=0,land_cover=row['land_cover'])
 if f['land_cover']<=0:raise ValueError('Missing verified land-cover lookup')
 features=models[0].feature_name()
 if any(m.feature_name()!=features or m.dump_model()['objective']!='regression' for m in models):raise ValueError('Unexpected model features or objective')
 x=pd.DataFrame([f])[features]
 if not np.isfinite(x.to_numpy()).all():raise ValueError('Nonfinite feature vector')
 # Original CyFi: mean in log(1+density) space, clamp negative log output, expm1, round.
 raw=[float(m.predict(x,num_threads=1)[0]) for m in models]
 prediction=float(np.round(np.expm1(max(0,float(np.mean(raw))))))
 if not np.isfinite(prediction):raise ValueError('Nonfinite model output')
 return {'status':'complete','density_cells_per_ml':prediction,'acquisition_date':row['acquisition_date'],'scene_id':row['scene_id'],'source_url':row['source_url'],'cloud_fraction':row['cloud_fraction'],'inside_fraction':row['inside_fraction'],'features':{k:float(f[k]) for k in features},'model_sha256':snapshot['model_sha256'],'fold_log_predictions':raw,'runtime_versions':snapshot['runtime_versions'],'quality_status':'Upstream spectral QC passed; geographic and radiometric transfer unvalidated'}
if __name__=='__main__':
 try:print(json.dumps(infer(sys.argv[1]),allow_nan=False))
 except Exception as e:print(json.dumps({'status':'withheld','density_cells_per_ml':None,'reason':str(e)}));sys.exit(1)
