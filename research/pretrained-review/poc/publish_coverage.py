"""Publish completed review checkpoints, preserving original eight observations."""
import json,sys,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from backend.config import write_json
from backend.cyfi import compute,available
OUT=ROOT/'output/cyfi-coverage-expansion'
before=json.loads((OUT/'inputs-before.json').read_text());snapshot=copy.deepcopy(before)
registry=json.loads((ROOT/'data/reservoirs.json').read_text());assert len(registry)==46
for r in registry:
 rid=r['id']
 if before['records'][rid]['status']=='eligible':continue
 path=OUT/f'checkpoints/{rid}.json'
 if not path.exists():raise RuntimeError(f'Missing checkpoint {rid}')
 state=json.loads(path.read_text())
 if not state['finished']:raise RuntimeError(f'Incomplete checkpoint {rid}')
 if state.get('approved'):
  row=state['approved'];row['preprocessing']={'bands':'Original CyFi configured native-grid crops','reflectance_scaling':'Raw delivered DN; no added scale, offset correction or clipping, matching original CyFi feature code','mask':'Original CyFi SCL water feature mask and cloud classes 7–10; extra 95% polygon-water diagnostic','compatibility':'Radiometric transfer and out-of-training-range inputs unresolved; not locally validated'}
  snapshot['records'][rid]=row
 else:
  attempts=state.get('attempts',[]);reason=state.get('reason') or '; '.join(dict.fromkeys(a.get('reason','') for a in attempts))
  row=copy.deepcopy(before['records'][rid]);row.update(status='rejected',reason=f'No approved CyFi input after {len(attempts)} acquisitions checked in the 2026-06-25–2026-10-23 window. {reason}')
  if attempts:row.update(scene_id=attempts[-1]['scene_id'],source_url=attempts[-1]['source_url'],acquisition_date=attempts[-1].get('acquisition_date'))
  snapshot['records'][rid]=row
assert {r['id'] for r in registry}==set(snapshot['records'])
for rid,row in before['records'].items():
 if row['status']=='eligible':assert snapshot['records'][rid]==row
write_json(ROOT/'data/cyfi/inputs-v1.json',snapshot)
results=[]
for rid,row in snapshot['records'].items():
 if row['status']=='eligible':
  result=compute(rid)
  if before['records'][rid]['status']=='eligible':
   old=json.loads((OUT/'protected.json').read_text())['predictions'][rid]
   assert result['density_cells_per_ml']==old['density_cells_per_ml'] and result['scene_id']==old['scene_id']
  else:
   expected=json.loads((OUT/f'checkpoints/{rid}.json').read_text())['inference']
   assert result.get('density_cells_per_ml')==expected['density_cells_per_ml'],(rid,result)
 results.append(available(rid));print(rid,results[-1]['status'],results[-1]['density_cells_per_ml'],flush=True)
write_json(OUT/'final-api-results.json',results)
