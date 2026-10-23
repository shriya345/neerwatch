"""Regression coverage for published genuine satellite inferences."""
import hashlib,json,math
from pathlib import Path
from backend.config import ROOT
from backend.cyfi import available,context

def test_coverage_keeps_original_eight_and_inventory():
 before=json.loads((ROOT/'output/cyfi-coverage-expansion/inputs-before.json').read_text())
 after=json.loads((ROOT/'data/cyfi/inputs-v1.json').read_text())
 assert set(before['records'])==set(after['records']) and len(after['records'])==46
 for rid,row in before['records'].items():
  if row['status']=='eligible':assert after['records'][rid]==row

def test_all_published_estimates_have_real_provenance_and_five_folds():
 for r in json.loads((ROOT/'data/reservoirs.json').read_text()):
  rid=r['id'];state=available(rid);_,row=context(rid)
  if row['status']!='eligible':
   assert state['density_cells_per_ml'] is None and state['reference_band']['label']=='Not assessed'
   assert state.get('reason')
   continue
  assert state['status']=='complete' and math.isfinite(state['density_cells_per_ml'])
  assert state['units']=='cells/mL' and state['acquisition_date']==row['acquisition_date']
  assert state['scene_id'] in state['source_url']
  assert len(state['fold_log_predictions'])==5 and len(state['features'])==30
  assert state['cloud_fraction']<=.05 and state['inside_fraction']>=.95
  for band,meta in row['band_files'].items():
   path=ROOT/row['cache_base']/f'sentinel_2000/{rid}/{row["scene_id"]}/{band}.npy'
   assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']

def test_protected_science_and_models_unchanged():
 before=json.loads((ROOT/'output/cyfi-coverage-expansion/protected.json').read_text())
 for name,sha in before['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha
