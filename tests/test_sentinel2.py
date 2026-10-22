import json
import numpy as np
import pytest
from backend.config import DATA
from backend.epa import classify
from pipeline.sentinel2_chlorophyll import gilerson
from vendor.waterqual.indices import compute_ndci
@pytest.mark.parametrize('value,name',[(0,'Oligotrophic'),(2,'Oligotrophic'),(2.0001,'Mesotrophic'),(7,'Mesotrophic'),(7.0001,'Eutrophic'),(30,'Eutrophic'),(30.0001,'Hypereutrophic')])
def test_epa_boundaries(value,name):assert classify(value)['name']==name
@pytest.mark.parametrize('value',[-1,float('nan'),float('inf'),None])
def test_epa_invalid(value):assert classify(value) is None

def test_real_krs_scene_outputs_and_reference_agreement():
 directory=DATA/'sentinel2/krs';rows=json.loads((directory/'history.json').read_text());assert len(rows)>=2
 for row in rows:
  pixels=np.load(directory/f"{row['item_id']}-bands.npz");mask=pixels['valid_mask'];b4=pixels['B04'];b5=pixels['B05']
  reference_ndci=(b5-b4)/(b5+b4)
  assert np.allclose(compute_ndci(b5,b4)[mask],reference_ndci[mask],rtol=1e-6,atol=1e-6)
  # Independent evaluation of FCMm BR_Gil10's published R expression on real pixels.
  expected=(35.75*(b5[mask]/b4[mask])-19.3)**1.124
  assert np.allclose(pixels['chlorophyll_a'][mask],expected,rtol=1e-5)
  assert np.isclose(row['chlorophyll_a'],np.median(expected),rtol=1e-5)
  assert (directory/row['rgb_file']).exists() and (directory/row['chlorophyll_map_file']).exists()
  import rasterio
  with rasterio.open(directory/row['chlorophyll_raster_file']) as src:
   assert src.tags()['scene_id']==row['item_id'];assert src.crs.to_epsg()==32643
   assert np.allclose(src.read(1)[mask],expected,rtol=1e-5)
  assert row['quality']['algorithm_valid_pixels']>=25 and row['quality']['algorithm_valid_fraction']>=.1

def test_invalid_algorithm_pixels_are_missing():
 assert np.isnan(gilerson(np.array([0.,.01,1.]),np.array([0.,1.,.001]))).all()

def test_no_sentinel3_substitution():
 from backend.active import monitoring
 assert monitoring('not-processed')['chlorophyll_a'] is None

def test_inventory_and_primary_api_contract():
 from fastapi.testclient import TestClient
 from backend.main import app
 client=TestClient(app)
 rows=client.get('/api/reservoirs').json()['items']
 assert 16<=len(rows)<=46
 additions=[r for r in rows if r.get('inventory_id')]
 assert not additions
 assert all(r['boundary_available'] for r in rows)
 response=client.get('/api/reservoirs/krs/report.pdf')
 assert response.status_code==200 and response.content.startswith(b'%PDF')
 from pypdf import PdfReader
 from io import BytesIO
 text=' '.join(p.extract_text() for p in PdfReader(BytesIO(response.content)).pages)
 assert 'Eutrophic' in text and '2026-10-12' in text and 'not yet been validated' in text
 assert client.get('/api/reservoirs/krs/sentinel2/raster').status_code==200
 assert client.get('/api/reservoirs/cwc-ka06lh0006/sentinel2/raster').status_code==404
