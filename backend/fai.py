"""Read a published immutable FAI snapshot, never active acquisition checkpoints."""
import json,math
from backend.config import DATA,today
SNAPSHOT=DATA/'fai-snapshots'/'observed-v1.json'
def observed(identifier):
 payload=json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else {'observations':{}}
 rows=payload['observations'].get(identifier,[])
 rows=[r for r in rows if isinstance(r.get('fai'),(int,float)) and math.isfinite(r['fai']) and r['observed_at'][:10]<=today().isoformat()]
 good=sorted([r for r in rows if r['qc']=='approved' and r['method']==payload.get('version')],key=lambda r:r['observed_at'])
 legacy=[r for r in rows if r['qc']!='approved']
 return {'units':'dimensionless','latest':good[-1] if good else None,'history':good,'legacy':legacy,'quality_status':'QC-approved snapshot' if good else 'Historical mask provenance incomplete' if legacy else 'No QC-approved observation','snapshot_version':payload.get('version'),'forecast':None,'warning':'Legacy observations lack saved SCL; excluded from comparable history.' if legacy else None}
