"""Review decisions using the real imported observation histories."""
import json
from backend.config import DATA
from backend.chlorophyll_review import review

def history(identifier):return json.loads((DATA/'observations'/f'{identifier}-chlorophyll.json').read_text())

def test_real_krs_decline_has_dates_values_and_no_trend_review():
    r=review(history('krs'));c=r['comparison']
    assert c['previous']['observed_at']=='2026-09-10'
    assert c['current']['observed_at']=='2026-09-20'
    assert round(c['previous']['chlorophyll_a'],2)==11.78
    assert round(c['current']['chlorophyll_a'],2)==7.01
    assert round(c['percent'],1)==-40.5
    assert r['required'] is False and r['trend_required'] is False
    assert not r['who']['applicable']

def test_real_tungabhadra_increase_requires_review_not_who_clearance():
    r=review(history('tungabhadra'))
    assert r['trend_required'] and r['required']
    assert r['who']['trigger_level_ug_l']==10
    assert not r['who']['applicable']
    assert 'Confirm cyanobacteria dominance' in r['who']['interpretation']

def test_decreasing_above_who_reference_still_needs_review():
    rows=history('krs')
    candidate=next(rows[:i+1] for i in range(1,len(rows)) if rows[i]['chlorophyll_a']>=10 and rows[i]['chlorophyll_a']<rows[i-1]['chlorophyll_a'])
    r=review(candidate)
    assert r['trend_required'] is False and r['required'] is True

def test_missing_concentrations_cannot_be_cleared():
    r=review([])
    assert r['required'] is None and r['status']=='Cannot determine'
    assert r['who']['status']=='Cannot compare'


def test_public_sentinel3_source_pixels_and_provider_flags():
    import numpy as np
    from pipeline.sentinel3_chlorophyll import REJECT
    from backend.monitoring import reservoirs
    for reservoir in reservoirs():
        if reservoir['priority'] or not (DATA/'observations'/f"{reservoir['id']}-chlorophyll.json").exists():continue
        rows=history(reservoir['id'])
        assert rows, f"No genuine concentration for {reservoir['id']}"
        for row in rows:
            assert row['encoding']['units']=='lg(re mg.m-3)'
            assert row['unit']=='µg/L'
            assert all(a['checksum_verified'] for a in row['source_assets'].values())
            assert row['quality']['valid_pixels']>=3 and row['quality']['valid_fraction']>=.1
            pixels=np.load(DATA/row['pixel_file']);accepted=pixels['accepted'];values=pixels['chlorophyll_a'][accepted]
            assert np.isclose(np.median(values),row['chlorophyll_a'])
            flags=row['quality']['flag_masks'];rejected=np.uint64(sum(flags[k] for k in REJECT))
            assert np.all((pixels['wqsf'][accepted]&rejected)==0)
            assert np.all((pixels['wqsf'][accepted]&np.uint64(flags['INLAND_WATER']))!=0)
            assert np.isfinite(values).all() and (values>0).all()
