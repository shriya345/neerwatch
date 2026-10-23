import json,math
import pytest
from fastapi.testclient import TestClient
from backend.cyfi_reference import reference_band
from backend.main import app
from backend import cyfi
@pytest.mark.parametrize('value,expected',[(0,'lower'),(19999,'lower'),(20000,'moderate'),(99999,'moderate'),(100000,'high'),(10000000,'high'),(10000001,'very_high')])
def test_exact_boundaries(value,expected):
 r=reference_band(value);assert r['id']==expected and r['assessed']
@pytest.mark.parametrize('value',[None,-1,float('nan'),float('inf'),float('-inf'),True,'0'])
def test_invalid_values_never_green(value):
 r=reference_band(value);assert r['id']=='not_assessed' and r['label']=='Not assessed' and not r['assessed']
@pytest.mark.parametrize('status',['withheld','unavailable','missing','ready','processing','failed',None])
def test_noncomplete_never_categorized(status):
 assert reference_band(0,status)['id']=='not_assessed'
def test_actual_three_estimates_lower():
 c=TestClient(app)
 for rid,n in [('krs',16652),('bhadra',16710),('supa',7105)]:
  d=c.get(f'/api/reservoirs/{rid}/cyfi').json()
  assert d['density_cells_per_ml']==n and d['reference_band']['label']=='Lower count band'
  assert d['operational_use'] is False
 for rid,row in json.loads(cyfi.SNAPSHOT.read_text())['records'].items():
  if row['status']=='eligible':continue
  d=c.get(f'/api/reservoirs/{rid}/cyfi').json();assert d['reference_band']['label']=='Not assessed' and d['density_cells_per_ml'] is None
@pytest.mark.parametrize('value',[None,-1,float('nan'),float('inf')])
def test_corrupt_cached_estimates_safe_for_json(value,tmp_path,monkeypatch):
 monkeypatch.setattr(cyfi,'CACHE',tmp_path)
 (tmp_path/'krs.json').write_text(json.dumps({'cache_key':cyfi.key(),'status':'complete','density_cells_per_ml':value}))
 r=TestClient(app).get('/api/reservoirs/krs/cyfi');assert r.status_code==200
 d=r.json();assert d['status']=='withheld' and d['density_cells_per_ml'] is None and d['reference_band']['id']=='not_assessed'
def test_reference_is_project_extension_and_display_only():
 d=cyfi.available('krs');assert 'project display extension' in d['reference_explanation']
 assert d['reference_source_url'].startswith('https://www.epa.gov/')
 from backend.config import ROOT
 text=(ROOT/'frontend/src/main.jsx').read_text().split('function ExperimentalML')[1].split('function App')[0]
 for required in ['Experimental cell-count reference bands','Experimental model estimate, not a laboratory measurement.','CyFi pretrained LightGBM regression ensemble','biovolume, chlorophyll-a, scums and toxins']:
  assert required in text
 for module in ['active.py','reports.py','monitoring.py']:
  assert 'cyfi_reference' not in (ROOT/'backend'/module).read_text()

@pytest.mark.parametrize('rid,count,band,date',[
 ('kabini',92348,'moderate','2026-10-12'),
 ('hemavathi',56982,'moderate','2026-10-12'),
 ('linganamakki',20834,'moderate','2026-10-12'),
 ('hidkal',48623,'moderate','2026-10-20'),
 ('gerusoppa',18648,'lower','2026-10-20'),
])
def test_additional_reviewed_inferences(rid,count,band,date):
 d=TestClient(app).get(f'/api/reservoirs/{rid}/cyfi').json()
 assert d['status']=='complete' and d['density_cells_per_ml']==count
 assert d['reference_band']['id']==band and d['acquisition_date'].startswith(date)
 assert d['cloud_fraction']<=.05 and d['inside_fraction']>=.95
 assert d['scene_id'] in d['source_url']
