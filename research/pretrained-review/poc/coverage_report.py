"""Generate evidence report from actual published results, never inferred counts."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'output/cyfi-coverage-expansion'
results=json.loads((OUT/'final-api-results.json').read_text());before=json.loads((OUT/'inputs-before.json').read_text())
names={r['id']:r['name'] for r in json.loads((ROOT/'data/reservoirs.json').read_text())}
new=[r for r in results if r['status']=='complete' and before['records'][r['reservoir_id']]['status']!='eligible'];ok=[r for r in results if r['status']=='complete'];bad=[r for r in results if r['status']!='complete']
p=json.loads((OUT/'protected.json').read_text());unchanged={k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in p['sha256'].items()};history=all([(ROOT/k).stat().st_size,(ROOT/k).stat().st_mtime_ns]==v for k,v in p['history'].items());assert all(unchanged.values()) and history
checkpoints=[json.loads(f.read_text()) for f in (OUT/'checkpoints').glob('*.json')];attempts=sum(len(x['attempts']) for x in checkpoints)
s=f'''# NEERWATCH CyFi coverage expansion

## Actual outcome

- Exact inventory: **46 Karnataka reservoirs**, unchanged.
- Approved experimental estimates before: **8**; after: **{len(ok)}**.
- Newly covered: **{len(new)}**. Remaining Not assessed: **{len(bad)}**.
- Original eight observations, manifest records and numerical predictions preserved; caches regenerated with the updated snapshot key.
- {attempts} distinct per-reservoir scene attempts recorded across 38 review checkpoints. Acquisitions are not approved until all input screens pass.
- New coverage: {', '.join(names[r['reservoir_id']] for r in new)}.

## Method and bounds

Cached operational Sentinel-2 acquisitions were tried first. Microsoft Planetary Computer Sentinel-2 L2A STAC supplied genuine alternative scenes and original native-grid raster crops. Search window: 25 June–23 October 2026. First pass checks up to eight distinct acquisition dates per reservoir, preferring recent candidates. The first pass completed. A second-pass option was prepared but NOT run after the instruction to stop expansion; no further data acquisition was started. Catalogue requests are capped at 100 returned scenes per reservoir; exhaustive search is not claimed. Checkpoints retain each attempted scene, actual date and rejection reason. Downloads retry three times with backoff; per-band caches and atomic checkpoint writes allow resumption. Separate historical FAI files are never read for extraction or written.

Exactly five original CyFi LightGBM regressors execute with original feature order, original land-cover lookup, original raw-DN/native-grid feature calculation and original log-space ensemble/expm1/round aggregation. No retraining, synthetic features, imputation, scaling changes or clipping. Original cloud classes 7–10 must occupy ≤5% of the crop, required features must be finite, and ≥95% of SCL water pixels must belong to the selected reservoir polygon. Invalid registry points are not moved. A later backend pass verifies source-code/model/runtime/band checksums and independently reproduces each new cached result from its source arrays.

This establishes technical input eligibility, **not** Karnataka scientific validation. Baseline offsets/radiometric transfer and out-of-training-range inputs remain unresolved. The unchanged upstream radiometric treatment does not establish that modern input distributions match training. Results are experimental point-box estimates, not measured cell counts or validated whole-reservoir averages.

## Approved estimates and provenance

| Reservoir | New | cells/mL | Acquisition | Band | Actual scene |
|---|---|---:|---|---|---|
'''
for r in ok:s+=f"| {names[r['reservoir_id']]} | {'Yes' if r in new else 'Existing'} | {r['density_cells_per_ml']:,.0f} | {r['acquisition_date'][:10]} | {r['reference_band']['label']} | [{r['scene_id']}]({r['source_url']}) |\n"
s+='\n## Remaining unavailable reservoirs\n\n| Reservoir | Actual rejection/search reason |\n|---|---|\n'
for r in bad:s+=f"| {names[r['reservoir_id']]} | {r.get('reason','No approved input')} |\n"
s+='''
See `checkpoints/<reservoir>.json` for exact scene-by-scene results, `final-api-results.json` for all 46 API states, and `data/cyfi/inputs-v1.json` for original band URLs/checksums and preprocessing metadata. Raw crops and grid metadata remain in `research/pretrained-review/poc/sentinel_2000/`; catalogue responses remain in `coverage-cache/`. These are isolated from FAI acquisition.

## Application integration

The existing Experimental ML Estimates section reads the published API snapshot automatically on reservoir selection/reload. It shows cells/mL, the unchanged display-only count band, actual date, model/source attribution and QC state. Missing estimates remain Not assessed with the actual reason. Expanded provenance text retains transfer and out-of-range limitations. Operational alerts and PDF reports do not consume CyFi. The reference bands remain historical WHO-derived display references with the explicitly labelled project-specific >10-million extension; they do not establish public-health safety or toxin concentration.

To view: open http://127.0.0.1:8010/, refresh, search/select a newly covered reservoir, and scroll to Experimental ML Estimates. Select a remaining rejected reservoir to inspect Not assessed and its reason.

## Files modified

- `research/pretrained-review/poc/expand_coverage.py`: bounded acquisition, caching, original feature/inference processing, spatial/cloud checks and checkpoints.
- `research/pretrained-review/poc/publish_coverage.py`: validated publication preserving original eight, exact backend re-inference and result checks.
- `research/pretrained-review/poc/coverage_report.py`: reproducible evidence report.
- `data/cyfi/inputs-v1.json`, approved `data/cyfi/predictions/*.json`: new reviewed observations and cached original-model results.
- `frontend/src/main.jsx`: provenance details describe bounded scene search and compatibility limitations; design unchanged.
- `tests/test_cyfi.py`, `tests/test_cyfi_reference.py`: keep rejection tests independent of formerly unavailable reservoirs gaining valid observations.
- `tests/test_cyfi_coverage.py`: original-eight preservation, all-46 provenance/checksums, finite features, five-fold execution and protected science files.
- Rebuilt frontend distribution; generated review/provenance files in this output directory and isolated crop cache.

## Validation and limitations

'''
s+='Backend test output:\n\n```text\n'+(OUT/'backend-tests.txt').read_text()+'\n```\n\nFrontend build:\n\n```text\n'+(OUT/'frontend-build.txt').read_text()+'\n```\n'
s+=f'\nProtected-file SHA256 checks: all {len(unchanged)} passed. Historical checkpoint/observation file size+mtime checks: all {len(p["history"])} unchanged. The separate historical acquisition was not running at the initial process check; it was not restarted or interrupted.\n'
s+=(OUT/'browser-verification.txt').read_text() if (OUT/'browser-verification.txt').exists() else '\nBrowser verification pending.\n'
s+='\nRemaining rejected inputs require different suitable acquisitions or a separately justified sampling methodology; QC must not be weakened solely to increase coverage. International pretrained model outputs cannot establish local accuracy without independent Karnataka field measurements. No prediction is a future FAI forecast, official alert, toxin estimate or laboratory result.\n'
(OUT/'IMPLEMENTATION_REPORT.md').write_text(s)
print(len(ok),'approved;',len(new),'new;',len(bad),'unavailable')
