import json
from backend.config import DATA
from backend.monitoring import reservoirs
from backend.active import monitoring

def test_scale_publication_count_pairs_and_originals():
 rows=reservoirs();ids={r['id'] for r in rows}
 assert len(rows)==len(ids)==46
 original=set(json.loads((DATA/'internal/original-sixteen-scale-snapshot.json').read_text()))
 assert original<=ids and len(ids-original)==30
 for r in rows:
  m=monitoring(r['id']);assert m['classification'] and m['change']
  assert m['previous']['observed_at'][:10]<m['latest']['observed_at'][:10]
  assert m['latest']['unit']=='µg/L'
  for row in [m['latest'],m['previous']]:assert (DATA/'sentinel2'/r['id']/f"{row['item_id']}-bands.npz").is_file()
  if r['id'] not in original:assert r['identity_verification']['identity_verified']

def test_media_is_pinned_to_requested_saved_acquisition():
 from fastapi.testclient import TestClient
 from backend.main import app
 client=TestClient(app);m=monitoring('basava-sagara');previous=m['previous']
 response=client.get('/api/reservoirs/basava-sagara/sentinel2/rgb',params={'scene_id':previous['item_id']})
 assert response.status_code==200
 assert response.content==(DATA/'sentinel2/basava-sagara'/previous['rgb_file']).read_bytes()
 assert client.get('/api/reservoirs/basava-sagara/sentinel2/rgb',params={'scene_id':'not-a-saved-scene'}).status_code==404
