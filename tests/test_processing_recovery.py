"""Regression checks for job loss, missing-concentration fallback and pagination.
Network conditions are isolated in these tests; live five-reservoir evidence
is recorded separately in output/processing-verification.json.
"""
import json
import shutil
from pathlib import Path
import numpy as np
import httpx
from backend.config import DATA
import pipeline.sentinel2_chlorophyll as service

FIXTURE=Path(__file__).parent/'fixtures/krs-stac-scenes.json'

def test_status_survives_restart_and_marks_interruption(tmp_path,monkeypatch):
 monkeypatch.setattr(service,'DATA',tmp_path);monkeypatch.setattr(service,'JOBS',{})
 service.save_job('test',status='failed',stage='failed',reason='Verified water polygon required')
 service.JOBS.clear()
 assert service.get_status('test')['reason']=='Verified water polygon required'
 service.save_job('test',status='running',stage='reading_B04');service.JOBS.clear()
 state=service.get_status('test')
 assert state['status']=='failed' and state['stage']=='interrupted'
 assert 'restart' in state['reason']
 assert json.loads((tmp_path/'sentinel2/test/job.json').read_text())['status']=='failed'

def test_failed_job_is_saved_with_specific_reason(tmp_path,monkeypatch):
 monkeypatch.setattr(service,'DATA',tmp_path);monkeypatch.setattr(service,'JOBS',{})
 class Immediate:
  def submit(self,fn):fn()
 monkeypatch.setattr(service,'POOL',Immediate())
 def fail(*args,**kwargs):raise service.ProcessingFailure('B04 source returned HTTP 503',[{'reason':'HTTP 503','item_id':'unavailable-source'}])
 monkeypatch.setattr(service,'process',fail)
 result=service.start('test',force=True)
 assert result['status']=='failed' and result['reason']=='B04 source returned HTTP 503'
 service.JOBS.clear()
 assert service.get_status('test')['attempts'][0]['reason']=='HTTP 503'

def test_search_follows_pagination(monkeypatch):
 from pipeline import satellite
 from datetime import date
 scenes=json.loads(FIXTURE.read_text());requests=[];Client=httpx.Client
 def respond(request):
  requests.append(request)
  if len(requests)==1:return httpx.Response(200,json={'features':[scenes[0]],'links':[{'rel':'next','href':satellite.STAC+'?token=next'}]})
  return httpx.Response(200,json={'features':[scenes[1]],'links':[]})
 monkeypatch.setattr(satellite.httpx,'Client',lambda **kwargs:Client(transport=httpx.MockTransport(respond)))
 found=satellite.search(scenes[0]['geometry'],date(2026,10,22),lookback=60,limit=1)
 assert len(found)==2 and len(requests)==2
 assert requests[0].url.params['sortby']=='-properties.datetime'

def test_invalid_concentration_does_not_stop_older_scene_search(tmp_path,monkeypatch):
 scenes=sorted(json.loads(FIXTURE.read_text()),key=lambda i:i['properties']['datetime'],reverse=True)
 (tmp_path/'boundaries').mkdir();shutil.copy(DATA/'boundaries/krs.geojson',tmp_path/'boundaries/krs.geojson')
 (tmp_path/'reservoirs.json').write_text((DATA/'reservoirs.json').read_text())
 monkeypatch.setattr(service,'DATA',tmp_path);monkeypatch.setattr(service,'search',lambda *a,**kw:scenes)
 calls=[]
 def read(item,*args,**kwargs):
  calls.append(item['id'])
  with np.load(DATA/'sentinel2/krs'/f"{item['id']}-bands.npz") as saved:
   bands={b:saved[b].copy() for b in ['B02','B03','B04','B05','B08','B11']}
   valid=saved['valid_mask'].copy();mask=saved['polygon_mask'].copy()
  if len(calls)==1:valid[:]=False # simulate an algorithm-domain rejection of the newest scene
  bands['_valid_water_mask']=valid
  return {'status':'available','quality':{},'source_url':item['links'][0]['href']},bands,mask
 monkeypatch.setattr(service,'read_item',read)
 result=service.process('krs',1)
 assert len(calls)==2 and result['item_id']==scenes[1]['id']
 assert result['chlorophyll_a'] is not None and result['epa_category'] is not None
 assert result['attempts'][0]['stage']=='chlorophyll_quality'
 latest=json.loads((tmp_path/'sentinel2/krs/latest.json').read_text())
 assert latest['item_id']==scenes[1]['id']
