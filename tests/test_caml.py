"""Checks against the supplied real CAML file and genuine acquired features.
No synthetic field data or fabricated labels are constructed.
"""
import hashlib,json
from pathlib import Path
import numpy as np,pandas as pd,pytest,joblib
from backend.config import DATA,MODEL
from pipeline.seabass import parse_seabass
from pipeline.features import FEATURE_NAMES
from pipeline.train import aligned_training,metrics
SOURCE=DATA/'caml/CAML_cyanobacteria_abundance_20211229_R1.sb'
@pytest.mark.skipif(not SOURCE.exists(),reason='Actual CAML file not supplied')
def test_supplied_file_roundtrip_and_metadata():
    frame,audit=parse_seabass(SOURCE)
    assert len(frame)==23570
    assert audit['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert audit['units']['abun']=='cells/L'
    assert frame.severity.value_counts().sort_index().to_dict()=={1:9761,2:4083,3:3812,4:5824,5:90}
    assert frame.distance_to_water_m.isna().sum()==1
    assert 'split' not in frame and 'density' not in frame
    assert not audit['competition_split_available']
@pytest.mark.skipif(not SOURCE.exists(),reason='Actual CAML file not supplied')
def test_abundance_conflict_is_preserved_without_guessing():
    frame,audit=parse_seabass(SOURCE)
    conflict=audit['abundance_audit']
    assert conflict['status']=='unresolved_source_unit_inconsistency'
    assert conflict['literal_conversion_disagreement_count']==13809
    assert frame.loc[frame.uid=='aabm','abun'].iloc[0]==.585
    assert frame.loc[frame.uid=='aabm','severity'].iloc[0]==1
    assert 'density' not in frame.columns
    assert not {'abun','severity','density','distance_to_water_m','region','data_provider'}&set(FEATURE_NAMES)
def test_genuine_matchups_are_strictly_historical():
    for p in (DATA/'cache/caml_training').glob('*.json'):
        result=json.loads(p.read_text())
        if result['status']!='available':continue
        delta=(pd.Timestamp(result['sample_date'])-pd.Timestamp(result['observed_at']).tz_localize(None).normalize()).days
        assert 1<=delta<=10
        assert result['quality']['valid_pixels']>=25
        assert result['quality']['valid_fraction']>=.1
        assert np.isfinite(list(result['features'].values())).all()
        assert result['source_url'].startswith('https://planetarycomputer.microsoft.com/')
@pytest.mark.skipif(not (MODEL/'metadata.json').exists(),reason='Genuine model not trained yet')
def test_real_holdout_metrics_and_training_scaler():
    meta=json.loads((MODEL/'metadata.json').read_text())
    split=pd.read_csv(MODEL/'split_manifest.csv');pred=pd.read_csv(MODEL/'test_predictions.csv')
    groups={name:set(part.geographic_group) for name,part in split.groupby('partition')}
    assert not groups['train']&groups['validation']
    assert not groups['train']&groups['test']
    assert not groups['validation']&groups['test']
    assert not split.uid.duplicated().any()
    assert set(pred.uid)==set(split[split.partition=='test'].uid)
    for key in ['mlp','random_forest']:
        recalculated=metrics(pred.supplied_severity,pred[key+'_prediction'])
        assert abs(recalculated['accuracy']-meta[key]['accuracy'])<1e-12
        assert abs(recalculated['macro_f1']-meta[key]['macro_f1'])<1e-12
        assert recalculated['confusion_matrix']==meta[key]['confusion_matrix']
    frame=aligned_training();train=frame[frame.uid.isin(split[split.partition=='train'].uid)]
    scaler=joblib.load(MODEL/'scaler.joblib')
    np.testing.assert_allclose(scaler.mean_,train[FEATURE_NAMES].mean().to_numpy(),atol=1e-12)
    assert meta['original_competition_split_used'] is False
    assert all(n>=2 for n in meta['partition_class_counts']['validation'].values())
    split_audit=json.loads((DATA.parent/'reports/caml_split_audit.json').read_text())
    assert split_audit['fixed_test_preserved'] is True
    assert sorted(pred.uid.tolist())==split_audit['fixed_test_uids']
    assert meta['abundance_unit_audit']['status']=='unresolved_source_unit_inconsistency'

@pytest.mark.skipif(not (MODEL/'metadata.json').exists(),reason='Genuine model not trained yet')
def test_dashboard_connected_estimates_remain_nonoperational():
    from backend.monitoring import summary,reservoirs
    for reservoir in reservoirs():
        data=summary(reservoir['id']);prediction=data['prediction']
        if data['latest'] is None:continue
        assert prediction['severity'] in [1,2,3,4,5]
        assert prediction['random_forest_severity'] in [1,2,3,4,5]
        assert 0<=prediction['class_probability']<=1
        assert prediction['numerical_density'] is None
        assert prediction['operational_use_supported'] is False
        assert 'severity estimate' not in data['recommendation']['reason']
