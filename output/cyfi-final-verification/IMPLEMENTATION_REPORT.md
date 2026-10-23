# NEERWATCH: final CyFi implementation and verification

## Decision: CONDITIONAL GO — research use only

The unchanged five-model CyFi pipeline is technically reproducible on real Karnataka Sentinel-2 crops. Its original raw-DN feature method, feature order, log target, inverse transform and output units have been verified. This permits a separated demonstration of the original estimator under the user's CONDITIONAL GO rule. **It does not establish radiometric transfer, biological accuracy, whole-reservoir representativeness or operational fitness.** Significant out-of-distribution inputs and absent local labels remain prominently disclosed. These uncertainties have not been reclassified as successful validation.

The previous review withheld production approval. This decision retains that restriction and enables only the newly authorized experimental section. No feature was clipped, shifted, rescaled or otherwise adjusted to obtain reassuring predictions. The unchanged upstream method remains the method used by the application.

## Implemented application

NEERWATCH retains its exact 46-reservoir inventory, existing chlorophyll-a calculation, dimensionless observed FAI, search, monitoring, alerts and PDF/CSV reports. A separate **Experimental ML Estimates** component calls the new CyFi API. It displays the actual satellite date, density units, source, quality status, model identity, MIT attribution and limitations. The input is a sampling box near a reservoir point, explicitly not a whole-reservoir average.

- `GET /api/reservoirs/{identifier}/cyfi`: cached experimental result, processing status or explicit reason for withholding/unavailability.
- `POST /api/reservoirs/{identifier}/cyfi`: queues actual inference from the reviewed local snapshot. One worker processes requests; no satellite downloads or training are started.
- Original native-band crops are checked by SHA-256. Original preprocessing source and model checksums are checked before inference. Missing/corrupt bands, missing runtime, nonfinite features or failed quality checks produce no density.
- The original ZIP and complete MIT license are preserved in `models/cyfi/`. Inference runs in the isolated CyFi runtime, keeping the monitoring application's dependency environment unchanged.
- Computed predictions are cached separately in `data/cyfi/predictions/`, with snapshot/model/worker cache identity. Existing report and alert code does not import the CyFi service.
- `data/cyfi/inputs-v1.json` is a frozen snapshot covering all 46 IDs: three eligible records, two rejected scenes and 41 explicitly unavailable records. It contains no prefilled model density. The backend recomputes densities using the original regressors.

## Actual test observations

| Reservoir | Acquisition | Original ensemble output | Decision |
|---|---|---:|---|
| KRS | 12 October 2026 | 16,652 cells/mL | Experimental only |
| Bhadra | 12 October 2026 | 16,710 cells/mL | Experimental only |
| Supa | 2026-10-20 | 7,105 cells/mL | Experimental only |
| Tungabhadra | 17 October 2026 | None | 58.62% upstream cloud fraction; withheld |
| Vani Vilasa Sagara | 2026-10-12 | None | 20.39% upstream cloud fraction; withheld |

These are original upstream-method outputs after verification, not “corrected” or locally validated values. Fixed previously processed scenes were tested; the CyFi integration does not claim automatic 30-day earlier-scene fallback or universal 46-reservoir prediction coverage. Rejected scenes remain recorded, rather than being silently replaced by an invented result.

## Scientific and technical evidence

1. **Authentic regressors:** ZIP SHA and repository commit are in inputs-v1.json and the previous repository-evidence.json. All five load; they contain 276, 170, 73, 207 and 132 trees. Objective is regression, not classification.
2. **Inputs:** B01–B09, B8A, B11, B12, AOT, WVP and SCL. The ordered 30 features are recorded in technical-audit.json. They include band means, AOT range, green percentiles, band ratios, four NDVI variants, water fraction, month, scene age and a verified 2020 C3S land-cover class.
3. **Exact output:** arithmetic mean of five predictions in log(1+density) space; negative log output bounded at zero as in upstream code; expm1 and rounding produce cells/mL. Features are not clipped to training ranges.
4. **Preprocessing:** original 2 km buffer on each side, native band crops, zero-as-no-data handling, SCL water selection and the upstream 5% cloud gate. The source's OpenCV SCL resizing is reproduced, not silently replaced. One scene per request means the original batch 1% winsorization would leave the values unchanged. The full 15-candidate search is not claimed.
5. **Radiometry:** upstream reads raw raster values. NEERWATCH's existing chlorophyll-a uses scaled reflectance; those reflectances are **not** passed to CyFi. [Copernicus documentation](https://sentiwiki.copernicus.eu/web/s2-processing) establishes the additive offset introduced with newer processing baselines. The current method reproduces CyFi's software contract, but an archive-level match to the training images' encoding is not established. It is not possible here to attribute every outlier uniquely to radiometry versus real optical conditions. No undocumented subtraction is treated as an approved correction.
6. **Distribution:** nine KRS and four Bhadra features exceeded each original booster's stored training bounds in the earlier audit; current per-reservoir ranges are recorded again. Bounds are a diagnostic, not calibrated uncertainty limits. Producing a number does not validate these inputs.
7. **Spatial scope:** the existing polygons are preserved. Diagnostic SCL overlays establish at least 95% same-polygon water-pixel attribution for the eligible records. Original feature masks are retained; small outside-polygon fractions and absent shoreline buffering remain limitations. More restrictive masks would change the feature distribution and would need evaluation.
8. **Dependency provenance:** upstream feature source and model artifacts are unchanged. The core runtime libraries were aligned to the checked-in CyFi uv.lock: LightGBM 4.6.0, NumPy 2.4.3, OpenCV 4.13.0.92, pandas 3.0.1, SciPy 1.17.1 and rioxarray 0.22.0. The worker enforces these versions, recorded in poc-environment.txt. Re-reading B04 and SCL for all three eligible reservoirs with the locked crop library exactly reproduced the cached arrays; all three model outputs remained unchanged. Exact historical training-environment equivalence is not established; current reproducibility is tested directly. No assertion that every dependency equals its 2024 training version is made.
9. **License:** MIT permits adaptation with copyright/license preservation. The full DrivenData license is included. Satellite and ancillary source provenance is retained; the model license is not represented as a replacement for data-provider terms.
10. **Independent validation:** the [CyFi paper](https://doi.org/10.25080/pdhk7238) reports U.S. training/evaluation. The [authors' guidance](https://blog.drivendata.org/blog/cyfi-small-water-bodies) recommends local validation. No independent Karnataka or Indian validation was established by this search. No local MAE, RMSE, R², health category or toxin prediction is claimed.

## Separate FAI forecasting

The existing RandomForestRegressor preparation code remains unchanged: frozen-input validation, 10-day target with 7–13-day tolerance, chronological partitions, target-window purging, persistence baseline, MAE/RMSE/R², per-reservoir/season evaluation and explicit training gates. The saved historical snapshot fails the gate; see fai-eligibility.json. This is an audit of that saved snapshot, not a claim about every acquisition currently being written. No model was trained and no forecast was fabricated. The ongoing acquisition process and its source/checkpoints were not changed.

## How to run this installed project

```sh
cd /Users/shriyahr/Documents/ChatGPT/Major/NEERWATCH
cd frontend
npm run build
cd ..
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

Open http://127.0.0.1:8010/ and select KRS, Bhadra or Supa to see the cached research estimate below observed FAI. Other reservoirs show specific missing/rejected-input explanations. If no valid cache exists, eligible records offer “Compute experimental estimate.” Stop only a previous dashboard server if port 8010 is occupied; leave the separate historical acquisition process running.

The existing isolated runtime is `research/pretrained-review/venv/bin/python`, with its local OpenMP library in `research/pretrained-review/omp`. Backend execution configures this automatically. `NEERWATCH_CYFI_PYTHON` can select an equivalent installed runtime. Source clones and large raster caches are local prerequisites, not an internet service automatically downloaded by the dashboard. See the POC README and environment manifest for reproduction.

Tests: `.venv/bin/python -m pytest tests -q`. There is no configured frontend test script. Build and source-level disclosure checks do not constitute visual browser verification; browser control is disabled in this session.

## Faculty explanation

NEERWATCH monitors exactly 46 Karnataka reservoirs using satellite observations. It retains chlorophyll-a estimates and observed Floating Algae Index as separate indicators. A research section now runs five genuine pretrained CyFi LightGBM regressors to estimate cyanobacterial cell density for reviewed satellite inputs. Three reservoirs currently have reproducible experimental outputs, while missing or cloudy inputs produce explicit unavailable messages. These estimates have not been validated against Karnataka laboratory measurements and do not influence operational alerts or reports. Future FAI forecasting remains a separate, untrained pipeline awaiting adequate historical data.

## Final test results

- **76 backend tests passed**, including eight CyFi tests, after dependency alignment. One existing Starlette/httpx deprecation warning; no failures.
- Frontend production build passed; no frontend test runner is configured.
- Live HTTP checks returned 200 for the dashboard, health, experimental results, existing PDF report and CSV export. Three cached results match fresh inference; rejected/missing cases contain no density.
- Registry hash unchanged; acquisition source hash unchanged; original acquisition PID 2340 remained alive at final verification. Only backend/main.py and frontend/src/main.jsx changed among the pre-existing application files recorded at the start. The new service/worker/test files are additional.
- Visual layout, actual browser search clicks and button clicks were **not** verified: local browser control is disabled. The queued POST-to-complete workflow was tested through FastAPI with real inference.

Important files: backend/cyfi.py, backend/main.py, pipeline/cyfi_inference.py, data/cyfi/inputs-v1.json, models/cyfi/model_v0.zip and LICENSE, frontend/src/main.jsx, tests/test_cyfi.py, pytest.ini. Architecture is supplied as both ARCHITECTURE.md (Mermaid) and ARCHITECTURE.svg.
