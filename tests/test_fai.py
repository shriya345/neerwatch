import hashlib,json
from pathlib import Path
import numpy as np,pandas as pd,pytest
from backend.config import DATA
from backend.fai import observed
from pipeline.fai_regression import pairs,split,eligibility,run

def test_inventory_snapshot_exact():
 s=json.loads((DATA/'fai-snapshots/observed-v1.json').read_text());r=json.loads((DATA/'reservoirs.json').read_text());assert len(r)==46;assert set(s['observations'])=={x['id'] for x in r};assert s['registry_sha256']==hashlib.sha256((DATA/'reservoirs.json').read_bytes()).hexdigest()
def test_fai_negative_dates_sources():
 for r in json.loads((DATA/'reservoirs.json').read_text()):
  x=observed(r['id']);assert x['units']=='dimensionless';assert x['forecast'] is None
  for o in x['history']:
   assert np.isfinite(o['fai']);assert o['source_url'].startswith('https://');assert o['item_id'] in o['source_url'] or o['item_id'].startswith('MOSAIC');assert pd.Timestamp(o['observed_at']);assert o['valid_pixels']>=25
 assert observed('krs')['latest']['fai']<0
 assert observed('varahi')['latest'] is None;assert len(observed('varahi')['legacy'])==2;assert observed('varahi')['warning']
def test_missing(monkeypatch,tmp_path):
 import backend.fai as f
 monkeypatch.setattr(f,'SNAPSHOT',tmp_path/'absent');assert f.observed('krs')['latest'] is None;assert f.observed('krs')['history']==[]
def test_january_gate_and_no_future_features():
 d=pd.DataFrame({'reservoir_id':['krs']*5,'date':pd.date_range('2022-01-01',periods=5,freq='10D',tz='UTC'),'fai':[-.01,.02,.03,.04,.05],'scene_id':list('abcde')});p=pairs(d);assert p.iloc[0].fai_current==.02;assert p.iloc[0].fai_previous==-.01;assert p.iloc[0].target==.03;assert not eligibility(d,split(p))['eligible']
def test_temporal_purge():
 p=pd.DataFrame({'issue_time':pd.to_datetime(['2024-12-25','2025-01-10','2025-12-25','2026-01-10'],utc=True),'target_time':pd.to_datetime(['2025-01-04','2025-01-20','2026-01-04','2026-01-20'],utc=True),'target_scene':list('abcd'),'reservoir_id':['krs']*4});s=split(p);assert len(s['train'])==0;assert list(s['validation'].target_scene)==['b'];assert list(s['test'].target_scene)==['d']
def test_api_preserves_chlorophyll():
 from backend.monitoring import summary
 from backend.active import monitoring
 x=summary('krs');assert x['sentinel2']==monitoring('krs');assert x['fai']['forecast'] is None;assert x['fai']['latest']['fai']==observed('krs')['latest']['fai']

def test_exact_fai_and_original_acquisition():
 from scipy.ndimage import binary_erosion,binary_dilation
 for rid in ['krs','bhadra']:
  o=observed(rid)['latest'];history=json.loads((DATA/'sentinel2'/rid/'history.json').read_text());h=next(x for x in history if x['item_id']==o['item_id']);assert o['observed_at']==h['observed_at'];assert o['source_url']==h['source_url']
  with np.load(DATA/'sentinel2'/rid/(o['item_id']+'-bands.npz')) as z:
   valid=binary_erosion(z['polygon_mask']&(z['_scl']==6))&~binary_dilation(np.isin(z['_scl'],[3,8,9,10]))
   for b in ['B04','B08','B11']:valid &= np.isfinite(z[b])&(z[b]>0)&(z[b]<=1)
   values=z['B08']-(z['B04']+(z['B11']-z['B04'])*(.842-.665)/(1.610-.665));assert o['fai']==float(np.median(values[valid]))

def test_training_refused_without_artifact(tmp_path):
 path=tmp_path/'frozen.csv';output=tmp_path/'model';pd.DataFrame({'reservoir_id':['krs']*5,'date':pd.date_range('2022-01-01',periods=5,freq='10D',tz='UTC'),'fai':[-.01,.02,.03,.04,.05],'scene_id':list('abcde'),'source_urls':['https://example.test/scene']*5,'valid_pixels':[30]*5,'valid_fraction':[.5]*5}).to_csv(path,index=False)
 with pytest.raises(ValueError,match='Training refused'):run(path,output,True)
 assert not output.exists()
