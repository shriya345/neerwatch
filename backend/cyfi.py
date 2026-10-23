"""Separate experimental ML service. Never used by monitoring, alerts or reports."""
import hashlib,json,os,subprocess,threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from backend.config import ROOT,DATA,write_json,today
SNAPSHOT=DATA/'cyfi/inputs-v1.json'
CACHE=DATA/'cyfi/predictions'
EXECUTOR=ThreadPoolExecutor(max_workers=1,thread_name_prefix='cyfi-research')
LOCK=threading.Lock();JOBS={}
DISCLAIMER='Experimental model estimate, not a laboratory measurement. Karnataka-specific field validation has not been established. Radiometric transfer and out-of-range inputs remain unresolved. Not for toxicity assessment, operational alerts or future FAI forecasting.'
def context(identifier):
 if identifier not in {r['id'] for r in json.loads((DATA/'reservoirs.json').read_text())}:raise KeyError(identifier)
 payload=json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else {'records':{}}
 row=payload['records'].get(identifier,{'status':'unavailable','reason':'No reviewed CyFi satellite inputs are available for this reservoir.'})
 return payload,row

def key():
 h=hashlib.sha256()
 for p in [SNAPSHOT,ROOT/'models/cyfi/model_v0.zip',ROOT/'pipeline/cyfi_inference.py']:
  if p.exists():h.update(p.read_bytes())
 return h.hexdigest()

def _available(identifier):
 payload,row=context(identifier)
 base={'reservoir_id':identifier,'experimental':True,'decision':'CONDITIONAL GO','units':'cells/mL','model':'CyFi — pretrained LightGBM regression ensemble','repository':'https://github.com/drivendataorg/cyfi','license':'MIT · © DrivenData Inc.','model_version':payload.get('model_version'),'disclaimer':DISCLAIMER,'density_cells_per_ml':None,'acquisition_date':row.get('acquisition_date'),'source_url':row.get('source_url'),'operational_use':False}
 if row.get('acquisition_date','')[:10]>today().isoformat():return {**base,'status':'withheld','reason':'Satellite date is in the future.'}
 if row['status']!='eligible':return {**base,'status':'withheld' if row['status']=='rejected' else 'unavailable','reason':row['reason']}
 with LOCK:job=JOBS.get(identifier)
 if job and not job.done():return {**base,'status':'processing'}
 path=CACHE/f'{identifier}.json'
 if path.exists():
  result=json.loads(path.read_text())
  if result.get('cache_key')==key():return {**base,**result}
 return {**base,'status':'ready','reason':'Reviewed inputs available. Compute the experimental estimate.'}

def present(state):
 from backend.cyfi_reference import reference_band,BANDS,SOURCE_URL,CURRENT_WHO_URL,EXPLANATION
 state=dict(state)
 band=reference_band(state.get('density_cells_per_ml'),state.get('status'))
 if not band['assessed']:
  state['density_cells_per_ml']=None
  if state.get('status')=='complete':
   state.update(status='withheld',reason='Cached estimate is missing or invalid; no reference band assigned.')
 return {**state,'reference_band':band,'reference_bands':BANDS,'reference_explanation':EXPLANATION,'reference_source_url':SOURCE_URL,'current_who_url':CURRENT_WHO_URL}

def available(identifier):
 return present(_available(identifier))

def compute(identifier):
 env=dict(os.environ);env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',DYLD_LIBRARY_PATH=str(ROOT/'research/pretrained-review/omp'))
 python=Path(os.environ.get('NEERWATCH_CYFI_PYTHON',str(ROOT/'research/pretrained-review/venv/bin/python')))
 try:
  if not python.exists():raise ValueError('CyFi research runtime is not installed; no estimate generated.')
  run=subprocess.run([str(python),str(ROOT/'pipeline/cyfi_inference.py'),identifier],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
  result=json.loads(run.stdout.strip().splitlines()[-1])
  if run.returncode and result.get('status')!='withheld':raise ValueError('CyFi inference failed')
 except Exception as e:result={'status':'withheld','density_cells_per_ml':None,'reason':f'Inference unavailable: {e}'}
 result['cache_key']=key();write_json(CACHE/f'{identifier}.json',result)
 return result

def start(identifier):
 state=available(identifier)
 if state['status'] not in ['ready','withheld']:return state
 _,row=context(identifier)
 if row['status']!='eligible':return state
 with LOCK:
  job=JOBS.get(identifier)
  if not job or job.done():JOBS[identifier]=EXECUTOR.submit(compute,identifier)
 return present({**state,'status':'processing','density_cells_per_ml':None})
