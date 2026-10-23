# Experimental cell-count reference bands — implementation and verification

Implemented 23 October 2026. Scope remains exactly the existing 46 Karnataka reservoirs.

## Display-only mapping

| Cells/mL | Reference label | Colour |
|---|---|---|
| 0 ≤ value < 20,000 | Lower count band | Green |
| 20,000 ≤ value < 100,000 | Moderate count band | Yellow |
| 100,000 ≤ value ≤ 10,000,000 | High count band | Red |
| value > 10,000,000 | Very high count band | Dark red |
| Missing, invalid, negative, nonfinite, withheld or incomplete | Not assessed | Grey |

The API is the single source of labels, boundaries and colours. Zero is legitimate only for a completed valid estimate. No operational alerts, PDF reports or existing chlorophyll-a/FAI computations consume this mapping.

Scientific attribution: [EPA historical WHO summary](https://www.epa.gov/habs/world-health-organization-who-1999-guideline-values-cyanobacteria-freshwater) supports the 20,000 and 100,000 reference values but does **not** state a 10,000,000 cutoff. The requested upper split is explicitly labelled a project display extension. These are not current WHO operational classifications or Karnataka legal limits. [WHO 2021 guidance](https://www.who.int/publications/i/item/9789240031302) uses additional indicators including biovolume, chlorophyll-a, scums and toxins. No toxin or public-health safety determination is made.

A persistent disclaimer states that these are experimental estimates, not laboratory measurements; Karnataka field validation, radiometric transfer and out-of-range inputs remain unresolved. The model name, acquisition date, quality status, source link and expandable band boundaries are visible.

## Genuine inference expansion

Eight additional existing reservoirs were tested using genuine Sentinel-2 crops, exact original upstream feature processing and the unchanged five pretrained CyFi LightGBM regressors. Five passed the existing input screens; three were withheld. No training, synthetic inputs, substitutions or corrective clipping were introduced. Spatial diagnostic requires ≥95% of SCL water pixels in the crop to lie within the reservoir polygon; upstream cloud fraction must be ≤5%, and required features finite. These checks establish input eligibility, not Karnataka predictive accuracy. The model estimates the upstream point-centred box, not a validated whole-reservoir mean.

Current coverage: **8 completed, 5 withheld, 33 without reviewed inputs**, total 46. Earlier acquisitions have not been exhaustively searched for the withheld reservoirs. No claim of all-46 prediction coverage is made.

| Reservoir | Status | Estimate cells/mL | Band | Acquisition |
|---|---|---:|---|---|
| KRS | complete | 16652.0 | Lower count band | 2026-10-12 |
| Bhadra | complete | 16710.0 | Lower count band | 2026-10-12 |
| Tungabhadra | withheld | — | Not assessed | 2026-10-17 |
| Supa | complete | 7105.0 | Lower count band | 2026-10-20 |
| Vani Vilasa Sagara | withheld | — | Not assessed | 2026-10-12 |
| Kabini | complete | 92348.0 | Moderate count band | 2026-10-12 |
| Harangi | withheld | — | Not assessed | 2026-10-17 |
| Hemavathi | complete | 56982.0 | Moderate count band | 2026-10-12 |
| Almatti | withheld | — | Not assessed | 2026-10-12 |
| Linganamakki | complete | 20834.0 | Moderate count band | 2026-10-12 |
| Hidkal | complete | 48623.0 | Moderate count band | 2026-10-20 |
| Nugu | withheld | — | Not assessed | 2026-10-17 |
| Gerusoppa | complete | 18648.0 | Lower count band | 2026-10-20 |

Tungabhadra and Vani Vilasa Sagara remain withheld for cloud/quality screening. New rejected crops: Harangi 40.64% cloud; Nugu 13.56% cloud. Almatti passes the cloud and polygon screens but upstream extraction produces nonfinite B08_mean and NDVI_B04/B05/B06/B07; no imputation was used. The API retains the upstream spectral-QC rejection reason.

Provenance: `data/cyfi/inputs-v1.json` contains all 46 entries, scene IDs, original band URLs/checksums, cloud fraction and spatial diagnostics. `research/pretrained-review/poc/expanded-results.json` and `expanded-spatial.json` record the eight attempted crops. Original crops are in that directory's `sentinel_2000/`. Eight regenerated cache files in `data/cyfi/predictions/` record model checksum, exact features, fold predictions and locked runtime versions. `final-api-results.json` records all 46 resulting API states.

## Files changed in this task

- `backend/cyfi_reference.py`: reusable finite-value/status validation and exact inclusive/exclusive band mapping.
- `backend/cyfi.py`: decorate API responses with reference metadata; suppress invalid cached densities and avoid stale assessed bands during processing.
- `frontend/src/main.jsx`: display-only reference badge, sources, scientific caveats, model name and Not assessed states.
- `frontend/src/style.css`: restrained reference-band styling.
- `tests/test_cyfi_reference.py`: 32 added tests covering required boundaries, invalid/status cases, cache serialization, actual original and expanded predictions, sources and isolation from alerts/reports.
- `research/pretrained-review/poc/run.py`, `spatial_qc.py`: selectable probe IDs/output names for isolated expansion.
- `data/cyfi/inputs-v1.json`, eight `data/cyfi/predictions/*.json`: reviewed inputs and genuine cached inference results.
- Rebuilt frontend distribution and new evidence files in this directory.

Other pre-existing uncommitted repository changes are not attributed to this task.

## Verification

- Full backend suite: **108 passed**, 1 pre-existing Starlette/httpx deprecation warning, 30.38 seconds. See `backend-tests.txt`.
- Frontend production build: **passed**, Vite 8.3.5, 17 modules. See `frontend-build.txt`.
- Live browser at http://127.0.0.1:8010/: visually verified KRS green Lower (16,652), Kabini yellow Moderate (92,348), Harangi grey Not assessed with rejection reason. Checked Varahi's missing-input message and absence of a density/category. Reservoir search/select works. Source citation, dates, disclaimer and model name are visible. Screenshots: `kabini-browser.png`, `harangi-not-assessed.png`.
- Bhadra (16,710) and Supa (7,105) Lower bands verified through actual API tests. High/Very high exact boundaries verified by tests; no reservoir value was fabricated for a screenshot.
- SHA256 checks preserve inventory, model archive, report and alert modules, historical acquisition code and observed FAI snapshot. All **16,133** protected file size/mtime records remained unchanged, including historical observations/checkpoints.
- The earlier historical acquisition process was not running when checked at task start; it was neither restarted nor interrupted. This task used a separate CyFi crop cache and did not alter historical checkpoints.

## Remaining limitations

Only eight reservoirs have approved experimental inference inputs in this snapshot. The remaining 38 correctly display Not assessed. Additional scene acquisition/review would be needed to extend coverage. None of these numerical outputs or colours constitutes local validation, a toxicity assessment, an official alert or a future-FAI forecast.
