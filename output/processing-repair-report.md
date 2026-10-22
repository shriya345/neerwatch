# Sentinel-2 processing repair — 22 October 2026

All five requested reservoirs completed fresh spectral retrieval through the FastAPI processing endpoint. All have valid concentrations and EPA categories; zero failed in this run. No Sentinel-3 values or KRS values were substituted.

## Confirmed root cause

The original React polling effect called setJob(complete), then awaited the reservoir GET, then guarded setData with its active flag. Because the effect depended on job.status, the complete transition invoked cleanup and set active=false before the GET returned. Thus the result refresh was discarded even though the backend had saved a result. The repaired code fetches/applies the summary before setting terminal job status.

Navigation also reset job to idle without reading backend status. Jobs existed only in an in-memory dictionary, so failures disappeared on restart. Status now persists in job.json; opening a reservoir restores its status, queued/running jobs resume polling, and interrupted jobs have an explicit retry reason.

Bhadra was already successfully cached at diagnosis (23.970575 µg/L, 12 October); its API returned HTTP 200 with the result. There was no evidence of a Bhadra band/algorithm failure. Tungabhadra was idle with an empty cache, and an earlier CLI log reported Incomplete reservoir footprint for T43PFT tiles (1.15% coverage). Fresh diagnosis found the same-acquisition T43PFS tile covers the polygon completely and retrieved a genuine concentration. The current retrieval did not reproduce a polygon/CRS failure.

## Live results

| Reservoir | Scene ID | Acquisition (UTC) | Valid water pixels | Algorithm-valid pixels | Median µg/L | EPA category | Status |
|---|---|---|---:|---:|---:|---|---|
| krs | `S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927` | 2026-10-12T05:17:39.024000Z | 17,505 | 17,505 | 24.72256 | Eutrophic | complete |
| bhadra | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 2026-10-12T05:17:39.024000Z | 25,065 | 25,065 | 23.97058 | Eutrophic | complete |
| tungabhadra | `S2C_MSIL2A_20261017T051821_R062_T43PFS_20261017T102804` | 2026-10-17T05:18:21.025000Z | 32,290 | 31,965 | 42.19335 | Hypereutrophic | complete |
| supa | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 2026-10-20T05:28:41.025000Z | 18,533 | 18,533 | 25.31980 | Eutrophic | complete |
| vani-vilasa | `S2B_MSIL2A_20261012T051739_R062_T43PFR_20261012T091927` | 2026-10-12T05:17:39.024000Z | 7,950 | 7,950 | 21.65385 | Eutrophic | complete |

Algorithm for every row: Gilerson 2010 two-band power equation (35.75 × B05/B04 − 19.3)^1.124, experimental Sentinel-2 L2A BOA screening adaptation. WaterQual supplies the NDCI implementation; its placeholder concentration coefficients are not used.

The 60-day search considers acquisitions newest first, follows STAC pagination, rejects incomplete (<95%) footprints, and checks every candidate rather than only the first 30 items. SCL/cloud/shoreline and reflectance QC remain unchanged. A scene failing concentration QC no longer terminates the search or qualifies for a successful same-day concentration cache. If all fail, specific errors and attempted scenes persist. A usable RGB-only scene can remain visible without a fabricated concentration.

The current scenes use EPSG:32643, a 60 m analysis grid, native L2A baseline 05.13, DN scale 0.0001 and offset −0.1. Per-band source URLs, native resolutions and scaling are in processing-verification.json and each scene manifest. B04 and B05 are retrieved as spectral arrays; RGB rendering is never used to calculate concentration. All five water masks were reconstructed from saved SCL and spectral data; each matched the persisted mask. Independently calculated spectral medians and GeoTIFF pixel values matched the API outputs.

## Browser and backend verification

The Bhadra processing button issued POST /api/reservoirs/bhadra/process-sentinel2?force=true and received HTTP 202. The other four also received 202 with their own IDs. Browser checks confirmed each reservoir shows its own date/concentration/category. Progress, queued jobs and partial results are visible. Reload/navigation restore job status. A final backend restart retained all five completed statuses and cached results. Specific failure persistence and restart interruption are covered by regression tests.

Backend tests: 49 passed. Frontend production build: passed. Additional regression checks cover status persistence, interrupted jobs, source-failure reasons, STAC pagination and continuing to an earlier scene when the newest concentration fails QC. The live audit script is scripts/verify_live_processing.py. Browser evidence: browser-processing-verification.json.

## Files modified

- frontend/src/main.jsx — fix completion race, immediate pending state, restore status on selection, queued/running polling, show stage and explicit failed state, stale-selection guard.
- backend/main.py — persistent processing-status endpoint, ID validation, explicit force refresh parameter.
- pipeline/sentinel2_chlorophyll.py — durable jobs/progress/errors, first-result publication, search all window candidates, valid-concentration fallback, plot serialization and per-scene provenance.
- pipeline/satellite.py — STAC pagination, band progress, saved SCL and scaling/CRS metadata, water-mask failure diagnostics.
- tests/test_processing_recovery.py and tests/fixtures/krs-stac-scenes.json — regression tests using real saved scene references.
- scripts/verify_live_processing.py — live spectral, mask, raster, API and category audit.

## Remaining blockers and limits

No processing blocker remains for these five reservoirs. The 23 inventory-only entries still lack verified water polygons and remain explicitly disabled; this repair did not add reservoirs or fabricate polygons. Full ACOLITE correction and Karnataka field validation remain absent. Satellite-derived chlorophyll-a estimates have not yet been validated against Karnataka field measurements. Results are experimental screening estimates, not laboratory concentrations or water-safety determinations.

EPA thresholds: ≤2 oligotrophic; >2–7 mesotrophic; >7–30 eutrophic; >30 hypereutrophic µg/L. Missing/invalid concentrations receive no category. Source: https://nationallakesassessment.epa.gov/webreport/#trophic-state.

Final continuation check: all five persisted jobs remained complete, the live API/spectral audit passed again, 49 backend tests passed and the frontend build passed. Browser automation became disabled in Work settings during the last recheck; earlier browser verification and the Bhadra completion screenshot remain the UI evidence.
