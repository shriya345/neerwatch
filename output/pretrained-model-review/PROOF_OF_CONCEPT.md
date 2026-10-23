# CyFi isolated proof-of-concept results

Completed 23 October 2026. **Two successful numerical inferences; one QC rejection. No production deployment.**

These are unvalidated pretrained cyanobacteria estimates, not field measurements or future FAI predictions. The experiment uses genuine Sentinel-2 bands and the exact required C3S land-cover raster. No training, label fabrication or missing-feature imputation was performed.

| Existing reservoir | Actual acquisition date | Experimental CyFi cells/mL | Upstream cloud fraction | Status |
|---|---|---:|---:|---|
| krs | 2026-10-12 | 16652.0 | 0.020% | EXPERIMENTAL_UPSTREAM_INFERENCE_ONLY |
| bhadra | 2026-10-12 | 16710.0 | 1.181% | EXPERIMENTAL_UPSTREAM_INFERENCE_ONLY |
| tungabhadra | 2026-10-17 | Withheld | 58.617% | BLOCKED |

## Scene provenance

- krs: [S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927). Requested date is the acquisition date; scene-age feature is zero.
- bhadra: [S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927). Requested date is the acquisition date; scene-age feature is zero.
- tungabhadra: [S2C_MSIL2A_20261017T051821_R062_T43PFS_20261017T102804](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261017T051821_R062_T43PFS_20261017T102804). Requested date is the acquisition date; scene-age feature is zero.

## What was verified

- The original ZIP loads five fitted regression boosters (276, 170, 73, 207 and 132 trees).
- All 15 required native raster bands were actually retrieved for each of three existing reservoirs: 45 cached arrays. Per-band source URLs and SHA-256 hashes are in results.json.
- KRS and Bhadra each supply 30 finite model features. The actual land-cover lookup returned class 210 at both points. It was not assigned from the reservoir names or assumed from their water masks.
- Both numeric results were separately recalculated from their saved feature tables and all five boosters, matching exactly after upstream rounding. This verifies computational reproducibility, not predictive accuracy.
- Tungabhadra's chosen scene has 58.617% upstream cloud fraction, exceeding CyFi's 5% gate. No density was emitted. Earlier-scene fallback was not exercised in this fixed-scene probe.
- The registry still contains 46 entries and its hash matches the start of the probe. The historical acquisition process was left running; its code/checkpoints were not modified.
- Production dashboard, APIs, chlorophyll and FAI implementations were not changed by this investigation. The application test suite/build were not rerun because this work is isolated; no dashboard or frontend validation is claimed.

## Why this is not production approval

Nine KRS and four Bhadra spectral features lie outside each booster's stored training ranges. The current scenes' radiometric encoding must be reconciled with the training data. The upstream mask lacks reservoir-polygon enforcement and shoreline buffering; diagnostic overlays found a small number of outside-polygon water pixels. Altering these feature masks also requires transfer evaluation.

No independent Karnataka field labels were used or found here. No Karnataka MAE, RMSE, R², confidence interval, toxicity interpretation or health category is claimed. These numerical results should remain in the research report, not be presented as validated dashboard measurements.

## Reproduction

Runner, cached inputs, exact feature tables and diagnostic scripts: `research/pretrained-review/poc/`. See its README.md for commands. Pinned repository commits and model artifact hashes are in repository-evidence.json; dependencies are in poc-environment.txt. Large raster caches and isolated dependencies are excluded from Git within the research directory.

Decision: **working experimental CyFi inference demonstrated; production integration NO-GO pending preprocessing/transfer checks.** Continue collecting legitimate local satellite history for the separate Random Forest future-FAI experiment.
