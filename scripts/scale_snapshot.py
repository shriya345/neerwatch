import json,hashlib
from backend.config import DATA,write_json
if (DATA/'internal/original-sixteen-scale-snapshot.json').exists():
 print('Original-sixteen baseline already exists; retained unchanged');raise SystemExit(0)
records=json.loads((DATA/'reservoirs.json').read_text());snap={}
for r in records:
 paths=[DATA/'sentinel2'/r['id']/'latest.json',DATA/'sentinel2'/r['id']/'history.json',DATA/'boundaries'/f"{r['id']}.geojson"]
 snap[r['id']]={str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
write_json(DATA/'internal/original-sixteen-scale-snapshot.json',snap)
