import json
import math
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import DATA
from backend.readiness import check
client=TestClient(app)
def test_every_public_workspace_is_complete():
 rows=client.get('/api/reservoirs').json()['items']
 assert {'krs','bhadra','tungabhadra','supa','vani-vilasa'} <= {r['id'] for r in rows}
 for row in rows:
  rid=row['id'];assert check(row)['ready'];assert 'tank' not in row['name'].lower()
  m=client.get(f'/api/reservoirs/{rid}').json()['sentinel2']
  assert m['latest']['observed_at'][:10]!=m['previous']['observed_at'][:10]
  assert m['chlorophyll_a']>0 and m['classification'] and math.isfinite(m['change']['percent'])
  assert math.isclose(m['change']['percent'],100*(m['chlorophyll_a']-m['previous']['chlorophyll_a'])/m['previous']['chlorophyll_a'])
  for kind in ['rgb','chlorophyll','raster']:assert client.get(f'/api/reservoirs/{rid}/sentinel2/{kind}').status_code==200
  assert client.get(f'/api/reservoirs/{rid}/boundary').status_code==200
  assert client.get(f'/api/reservoirs/{rid}/report.pdf').status_code==200

def test_pending_entries_are_not_publicly_accessible():
 ids={r['id'] for r in client.get('/api/reservoirs').json()['items']}
 for row in json.loads((DATA/'internal/pending-reservoirs.json').read_text()):
  rid=row['id'];assert rid not in ids
  for suffix in ['', '/boundary','/processing','/report.pdf','/sentinel2/rgb']:
   assert client.get(f'/api/reservoirs/{rid}{suffix}').status_code==404
  assert client.post(f'/api/reservoirs/{rid}/process-sentinel2').status_code==404
  assert row['name'] not in client.get('/api/chlorophyll-review.csv').text
