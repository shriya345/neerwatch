# Observed FAI implementation

Implemented 23 October 2026. Inventory remains exactly the existing 46 reservoirs. Existing chlorophyll retrieval, alerts, reports, search and citations were preserved.

## Implemented

- New `pipeline/fai_snapshot.py` validates existing operational Sentinel-2 arrays and publishes `data/fai-snapshots/observed-v1.json` atomically. It never reads/writes the actively acquired `data/fai-history` files. This initial snapshot uses the existing 92 operational observations; it is not a publication of the incomplete January acquisition run. Source bytes are checked for changes during snapshot construction, and array hashes are retained.
- New `backend/fai.py` exposes the frozen observed indicator through the existing reservoir detail response. Same-method QC-approved rows are the only comparable history. No future-FAI prediction is supplied.
- Dashboard section displays dimensionless FAI, signed values, actual acquisition date, source link, QC status and approved history. FAI axis labels use five decimal places. No concentration units, severity thresholds or FAI alerts were introduced.
- 45 reservoirs have two QC-approved observations each. Varahi remains selectable, with its two legacy values in an explicit incomplete-provenance disclosure; they are excluded from approved history/trends. The active acquisition may eventually provide reproducible Varahi replacements, but these must be published in a new validated snapshot before use.

## Prepared, not trained

`pipeline/fai_regression.py` provides frozen CSV validation, historical-only features, fixed ten-day targets with 7–13-day matching tolerance, shared chronological boundaries, a 13-day boundary purge, deduplication of repeated targets, persistence comparison, physical-unit MAE/RMSE/R², reservoir/season evaluation and artifact/metadata saving. Undefined R² is null, not fabricated.

Default invocation only audits eligibility:

```
.venv/bin/python -m pipeline.fai_regression /path/to/frozen-history.csv
```

Training requires explicit `--train` and passing gates: all five years, adequate independent targets, reservoir diversity and season coverage in every partition. Current January-only data fail. No trained artifact or dashboard forecast exists. Future deployment requires review of held-out skill and applicability, not merely creation of a model file. Future observed FAI remains a satellite proxy target, not field biomass.

A new stable historical export must be validated before future training. Never pass active per-scene checkpoints directly to the loader. Cutoffs are train through 2024, validation 2025, test 2026; target windows crossing boundaries are excluded. The fixed RF configuration avoids test-informed tuning. Data/feature hashes and software versions accompany any future authorized trained artifact.

## Verification

Existing full backend suite plus initial FAI tests: **66 passed** (one upstream Starlette/httpx deprecation warning). Two further focused tests independently reproduce FAI from saved bands and verify training refusal creates no model artifact. Frontend production build succeeded.

Live HTTP checks: KRS, Bhadra and Varahi detail responses returned 200 with expected FAI/QC and retained chlorophyll concentrations; KRS PDF returned 200. KRS observed FAI −0.0013273023068904877; Bhadra −0.0019520670175552368. Browser visual verification could not run because local browser control is disabled; do not claim visual end-to-end verification.

The pre-existing acquisition process was left running with its checkpoints untouched. No inventory edits, international lake changes or model training were performed.
