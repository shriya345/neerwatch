import json,hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import cyfi
from backend.config import DATA,ROOT
client=TestClient(app)
def test_registry_and_snapshot_exact():
 s=json.loads(cyfi.SNAPSHOT.read_text());r=json.loads((DATA/'reservoirs.json').read_text())
 assert len(r)==46 and set(s['records'])=={x['id'] for x in r}
 assert s['registry_sha256']==hashlib.sha256((DATA/'reservoirs.json').read_bytes()).hexdigest()
 assert s['model_sha256']==hashlib.sha256((ROOT/'models/cyfi/model_v0.zip').read_bytes()).hexdigest()
def test_actual_original_model_inference(tmp_path,monkeypatch):
 monkeypatch.setattr(cyfi,'CACHE',tmp_path)
 for rid,expected in [('krs',16652),('bhadra',16710),('supa',7105)]:
  r=cyfi.compute(rid)
  assert r['status']=='complete' and r['density_cells_per_ml']==expected
  assert len(r['fold_log_predictions'])==5 and len(r['features'])==30
  a=cyfi.available(rid)
  assert a['units']=='cells/mL' and a['experimental'] and a['operational_use'] is False
  assert a['acquisition_date']==json.loads(cyfi.SNAPSHOT.read_text())['records'][rid]['acquisition_date']
  assert a['scene_id'] in a['source_url']
def test_rejections_and_unknown(monkeypatch):
 original=cyfi.context
 def rejected(identifier):
  payload,row=original(identifier)
  return payload,{**row,'status':'rejected','reason':'Cloud quality failed'}
 monkeypatch.setattr(cyfi,'context',rejected)
 for rid in ['tungabhadra','vani-vilasa']:
  r=client.post(f'/api/reservoirs/{rid}/cyfi').json()
  assert r['status']=='withheld' and r['density_cells_per_ml'] is None and 'Cloud' in r['reason']
 assert client.get('/api/reservoirs/not-real/cyfi').status_code==404
 assert client.post('/api/reservoirs/not-real/cyfi').status_code==404
def test_missing_runtime_withheld(tmp_path,monkeypatch):
 monkeypatch.setattr(cyfi,'CACHE',tmp_path);monkeypatch.setenv('NEERWATCH_CYFI_PYTHON',str(tmp_path/'absent'))
 r=cyfi.compute('krs');assert r['density_cells_per_ml'] is None and r['status']=='withheld'
def test_alerts_reports_independent():
 from backend.monitoring import summary
 from backend.active import monitoring
 before=summary('krs');client.get('/api/reservoirs/krs/cyfi');after=summary('krs')
 assert before==after and after['sentinel2']==monitoring('krs')
 assert after['fai']['units']=='dimensionless' and after['fai']['forecast'] is None
 r=client.get('/api/reservoirs/krs/report.pdf');assert r.status_code==200 and r.content.startswith(b'%PDF')
 assert client.get('/api/chlorophyll-review.csv').status_code==200
 assert 'cyfi' not in (ROOT/'backend/reports.py').read_text().lower()
def test_ui_disclosures_and_no_thresholds():
 text=(ROOT/'frontend/src/main.jsx').read_text();component=text.split('function ExperimentalML')[1].split('function App')[0]
 assert 'Experimental ML Estimates' in component and 'cells/mL' in component
 assert 'Experimental model estimate, not a laboratory measurement.' in component
 assert 'RESEARCH ONLY' in component and 'not a whole-reservoir average' in component
 assert 'severity' not in component and 'µg/L' not in component
def test_request_runs_real_inference_and_caches(tmp_path,monkeypatch):
 monkeypatch.setattr(cyfi,'CACHE',tmp_path)
 r=client.post('/api/reservoirs/krs/cyfi');assert r.status_code==202 and r.json()['status']=='processing'
 cyfi.JOBS['krs'].result(timeout=30)
 r=client.get('/api/reservoirs/krs/cyfi').json()
 assert r['status']=='complete' and r['density_cells_per_ml']==16652
 assert (tmp_path/'krs.json').exists()
def test_real_worker_missing_bands_fails_closed(tmp_path):
 import shutil,subprocess,os
 for rel in ['data/cyfi/inputs-v1.json','data/reservoirs.json','models/cyfi/model_v0.zip']:
  dest=tmp_path/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
 env=dict(os.environ,DYLD_LIBRARY_PATH=str(ROOT/'research/pretrained-review/omp'),OMP_NUM_THREADS='1')
 code=f"from pathlib import Path\nimport pipeline.cyfi_inference as m\nm.ROOT=Path({str(tmp_path)!r})\ntry: m.infer('krs')\nexcept ValueError as e: assert 'Missing original satellite band' in str(e)\nelse: raise AssertionError('Missing bands accepted')"
 subprocess.run([str(ROOT/'research/pretrained-review/venv/bin/python'),'-c',code],cwd=ROOT,env=env,check=True,capture_output=True,text=True,timeout=30)
