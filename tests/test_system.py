"""Boundary, missing-data and real-observation integrity tests.
No fabricated training records or dashboard measurements are created.
"""
import json,math
import pytest
from fastapi.testclient import TestClient
from shapely.geometry import shape
from backend.main import app
from backend.config import DATA,CYANO_SOURCE,CHL_SOURCE,THRESHOLDS,CHL_THRESHOLDS,today
from backend.monitoring import reservoirs,summary
from pipeline.features import density_to_severity,FEATURE_NAMES
from pipeline.train import read_labels
client=TestClient(app)
@pytest.mark.parametrize('density,expected',[(0,1),(19999,1),(20000,2),(99999,2),(100000,3),(999999,3),(1000000,4),(9999999,4),(10000000,5)])
def test_official_class_boundaries(density,expected):assert density_to_severity(density)==expected
@pytest.mark.parametrize('density',[-1,float('nan'),float('inf')])
def test_invalid_density_rejected(density):
    with pytest.raises(ValueError):density_to_severity(density)
def test_no_invented_predictions():
    if not (DATA.parent/'models/metadata.json').exists():
        for reservoir in reservoirs():
            data=summary(reservoir['id']);assert data['prediction']['severity'] is None;assert data['model']['metrics'] is None
            assert 'forecast' not in data
def test_real_registry():
    items=reservoirs();assert len(items)>=5;assert {r['id'] for r in items if r['priority']}=={'krs','bhadra','supa','tungabhadra'}
    for r in items:
        assert r['state']=='Karnataka'
        if r['boundary_available']:
            feature=json.loads((DATA/'boundaries'/f"{r['id']}.geojson").read_text());polygon=shape(feature['geometry']);assert polygon.is_valid and not polygon.is_empty
            assert 11<r['latitude']<19 and 73<r['longitude']<79
            assert feature['properties']['source_url'].startswith('https://www.openstreetmap.org/')
def test_real_observation_provenance_and_quality():
    for reservoir in reservoirs():
        data=summary(reservoir['id']);windows=[o.get('query_end') for o in data['observations']]
        assert len(windows)==len(set(windows))
        for obs in data['observations']:
            if obs['status']!='available':continue
            assert obs['source_url'].startswith('https://planetarycomputer.microsoft.com/')
            assert obs['observed_at'][:10]<=obs['query_end']<=today().isoformat()
            assert obs['quality']['valid_pixels']>=25 and obs['quality']['valid_fraction']>=.1
            assert set(FEATURE_NAMES)==set(obs['features'])
            assert all(math.isfinite(v) for v in obs['features'].values())
            assert obs['chlorophyll_a'] is None
        for m in data['monthly']:assert m['valid_observations']+m['missing_windows']==m['acquisition_windows']
def test_exact_captions():
    assert all(t['source']==CYANO_SOURCE for t in THRESHOLDS)
    assert all(t['source']==CHL_SOURCE for t in CHL_THRESHOLDS)
def test_api():
    assert client.get('/api/health').json()['synthetic_data'] is False
    assert len(client.get('/api/reservoirs').json()['items'])>=5
    assert client.get('/api/reservoirs/not-a-reservoir').status_code==404
    r=client.get('/api/reservoirs/bhadra');assert r.status_code==200
    assert r.json()['reservoir']['name']=='Bhadra'
def test_missing_training_data_guard(tmp_path):
    with pytest.raises(ValueError,match='Genuine DrivenData data required'):read_labels(tmp_path)
def test_pdf_generation():
    response=client.get('/api/reservoirs/bhadra/report.pdf');assert response.status_code==200
    assert response.content.startswith(b'%PDF-') and len(response.content)>5000

def test_weather_flags_preserve_provider_values():
    for reservoir in reservoirs():
        for row in summary(reservoir["id"])["weather"]["rows"]:
            raw=row.get("provider_rainfall_mm")
            if raw is not None and raw>=200:
                assert row["rainfall_mm"] is None
                assert "rainfall_mm_requires_source_review" in row["quality_flags"]
