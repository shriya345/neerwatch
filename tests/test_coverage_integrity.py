import json,hashlib
from backend.config import DATA
from backend.monitoring import reservoirs
from backend.readiness import check

def test_original_eight_outputs_preserved():
 for rid,files in json.loads((DATA/'internal/original-eight-coverage-snapshot.json').read_text()).items():
  for name,digest in files.items():
   path=DATA/'boundaries'/name if name.endswith('.geojson') else DATA/'sentinel2'/rid/name
   assert hashlib.sha256(path.read_bytes()).hexdigest()==digest

def test_added_reservoir_identities_and_complete_pairs():
 assert 16<=len(reservoirs())<=46
 original=set(json.loads((DATA/'internal/original-eight-coverage-snapshot.json').read_text()))
 for record in reservoirs():
  if record['id'] in original:continue
  assert record['identity_verification']['identity_verified']
  assert record['identity_verification']['government_source'].startswith('https://')
  assert check(record)['ready']
