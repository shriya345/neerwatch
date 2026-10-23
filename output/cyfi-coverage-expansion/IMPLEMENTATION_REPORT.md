# NEERWATCH CyFi coverage expansion

## Actual outcome

- Exact inventory: **46 Karnataka reservoirs**, unchanged.
- Approved experimental estimates before: **8**; after: **32**.
- Newly covered: **24**. Remaining Not assessed: **14**.
- Original eight observations, manifest records and numerical predictions preserved; caches regenerated with the updated snapshot key.
- 157 distinct per-reservoir scene attempts recorded across 38 review checkpoints. Acquisitions are not approved until all input screens pass.
- New coverage: Tungabhadra, Varahi, Harangi, Almatti, Yagachi, Nugu, Basava Sagara, Karanja, Manchanabele, Taraka, Votehole, Chandrampalli, Dharma, Upper Tunga, Chikkahole, Chiklihole, Hattikuni, Narihalla, Upper Mullamari, Gandorinala, Maskinala, Chulkinala, Jambhadhahalla, Savehaklu.

## Method and bounds

Cached operational Sentinel-2 acquisitions were tried first. Microsoft Planetary Computer Sentinel-2 L2A STAC supplied genuine alternative scenes and original native-grid raster crops. Search window: 25 June–23 October 2026. First pass checks up to eight distinct acquisition dates per reservoir, preferring recent candidates. The first pass completed. A second-pass option was prepared but NOT run after the instruction to stop expansion; no further data acquisition was started. Catalogue requests are capped at 100 returned scenes per reservoir; exhaustive search is not claimed. Checkpoints retain each attempted scene, actual date and rejection reason. Downloads retry three times with backoff; per-band caches and atomic checkpoint writes allow resumption. Separate historical FAI files are never read for extraction or written.

Exactly five original CyFi LightGBM regressors execute with original feature order, original land-cover lookup, original raw-DN/native-grid feature calculation and original log-space ensemble/expm1/round aggregation. No retraining, synthetic features, imputation, scaling changes or clipping. Original cloud classes 7–10 must occupy ≤5% of the crop, required features must be finite, and ≥95% of SCL water pixels must belong to the selected reservoir polygon. Invalid registry points are not moved. A later backend pass verifies source-code/model/runtime/band checksums and independently reproduces each new cached result from its source arrays.

This establishes technical input eligibility, **not** Karnataka scientific validation. Baseline offsets/radiometric transfer and out-of-training-range inputs remain unresolved. The unchanged upstream radiometric treatment does not establish that modern input distributions match training. Results are experimental point-box estimates, not measured cell counts or validated whole-reservoir averages.

## Approved estimates and provenance

| Reservoir | New | cells/mL | Acquisition | Band | Actual scene |
|---|---|---:|---|---|---|
| KRS | Existing | 16,652 | 2026-10-12 | Lower count band | [S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927) |
| Bhadra | Existing | 16,710 | 2026-10-12 | Lower count band | [S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927) |
| Tungabhadra | Yes | 7,073 | 2026-10-12 | Lower count band | [S2B_MSIL2A_20261012T051739_R062_T43PFS_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFS_20261012T091927) |
| Supa | Existing | 7,105 | 2026-10-20 | Lower count band | [S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804) |
| Varahi | Yes | 16,001 | 2026-10-12 | Lower count band | [S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927) |
| Kabini | Existing | 92,348 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927) |
| Harangi | Yes | 35,562 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927) |
| Hemavathi | Existing | 56,982 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PFQ_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFQ_20261012T091927) |
| Almatti | Yes | 39,250 | 2026-09-27 | Moderate count band | [S2C_MSIL2A_20260927T051651_R062_T43QEU_20260927T101415](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20260927T051651_R062_T43QEU_20260927T101415) |
| Linganamakki | Existing | 20,834 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927) |
| Yagachi | Yes | 12,934 | 2026-09-27 | Lower count band | [S2C_MSIL2A_20260927T051651_R062_T43PEQ_20260927T101415](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20260927T051651_R062_T43PEQ_20260927T101415) |
| Hidkal | Existing | 48,623 | 2026-10-20 | Moderate count band | [S2C_MSIL2A_20261020T052841_R105_T43PDT_20261020T101804](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261020T052841_R105_T43PDT_20261020T101804) |
| Nugu | Yes | 46,936 | 2026-09-27 | Moderate count band | [S2C_MSIL2A_20260927T051651_R062_T43PFP_20260927T101415](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20260927T051651_R062_T43PFP_20260927T101415) |
| Basava Sagara | Yes | 21,437 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43QFU_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QFU_20261012T091927) |
| Gerusoppa | Existing | 18,648 | 2026-10-20 | Lower count band | [S2C_MSIL2A_20261020T052841_R105_T43PDR_20261020T101804](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261020T052841_R105_T43PDR_20261020T101804) |
| Karanja | Yes | 35,048 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927) |
| Manchanabele | Yes | 46,535 | 2026-10-14 | Moderate count band | [S2C_MSIL2A_20261014T050751_R019_T43PGQ_20261014T100514](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261014T050751_R019_T43PGQ_20261014T100514) |
| Taraka | Yes | 30,757 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927) |
| Votehole | Yes | 21,920 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PEQ_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PEQ_20261012T091927) |
| Chandrampalli | Yes | 23,504 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927) |
| Dharma | Yes | 18,076 | 2026-10-09 | Lower count band | [S2A_MSIL2A_20261009T052241_R062_T43PDS_20261009T101803](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2A_MSIL2A_20261009T052241_R062_T43PDS_20261009T101803) |
| Upper Tunga | Yes | 40,367 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927) |
| Chikkahole | Yes | 141,013 | 2026-10-14 | High count band | [S2C_MSIL2A_20261014T050751_R019_T43PGP_20261014T100514](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261014T050751_R019_T43PGP_20261014T100514) |
| Chiklihole | Yes | 95,040 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927) |
| Hattikuni | Yes | 560,209 | 2026-10-12 | High count band | [S2B_MSIL2A_20261012T051739_R062_T43QGU_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QGU_20261012T091927) |
| Narihalla | Yes | 37,714 | 2026-09-27 | Moderate count band | [S2C_MSIL2A_20260927T051651_R062_T43PFS_20260927T101415](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20260927T051651_R062_T43PFS_20260927T101415) |
| Upper Mullamari | Yes | 201,497 | 2026-10-12 | High count band | [S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927) |
| Gandorinala | Yes | 65,716 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927) |
| Maskinala | Yes | 181,883 | 2026-10-12 | High count band | [S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927) |
| Chulkinala | Yes | 261,880 | 2026-10-12 | High count band | [S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927) |
| Jambhadhahalla | Yes | 37,648 | 2026-10-12 | Moderate count band | [S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927) |
| Savehaklu | Yes | 14,499 | 2026-10-12 | Lower count band | [S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927) |

## Remaining unavailable reservoirs

| Reservoir | Actual rejection/search reason |
|---|---|
| Vani Vilasa Sagara | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 20.3926% exceeds original 5% limit; Cloud fraction 12.9277% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 19.4809% exceeds original 5% limit; Cloud fraction 35.5798% exceeds original 5% limit; Cloud fraction 7.7909% exceeds original 5% limit; Cloud fraction 8.5849% exceeds original 5% limit |
| Markonahalli | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 58.4500% exceeds original 5% limit; Cloud fraction 43.3571% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 99.4952% exceeds original 5% limit; Cloud fraction 10.9325% exceeds original 5% limit; Cloud fraction 27.2350% exceeds original 5% limit |
| Kadra | No approved CyFi input after 0 acquisitions checked in the 2026-06-25–2026-10-23 window. Invalid boundary or registry point outside polygon; no replacement point guessed |
| Malaprabha (Renuka Sagara) | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 73.3596% exceeds original 5% limit; Cloud fraction 5.2103% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 7.1162% exceeds original 5% limit; Only 89.1334% of SCL water belongs to reservoir polygon; minimum 95%; Cloud fraction 6.1409% exceeds original 5% limit; Only 90.0660% of SCL water belongs to reservoir polygon; minimum 95%; Only 90.6423% of SCL water belongs to reservoir polygon; minimum 95% |
| Kodasalli | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Original feature QC missing/nonfinite: B08_mean, NDVI_B04, NDVI_B05, NDVI_B06, NDVI_B07; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 95.0002% exceeds original 5% limit; Cloud fraction 14.4500% exceeds original 5% limit |
| Kanva | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 30.5632% exceeds original 5% limit; Cloud fraction 17.6821% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 15.3955% exceeds original 5% limit |
| Suvarnavathy | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 24.3054% exceeds original 5% limit; Cloud fraction 19.6341% exceeds original 5% limit; Cloud fraction 75.2506% exceeds original 5% limit; Cloud fraction 99.9830% exceeds original 5% limit; Cloud fraction 56.7789% exceeds original 5% limit; Cloud fraction 66.6748% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit |
| Bennethora | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 22.3727% exceeds original 5% limit; Cloud fraction 6.7082% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 12.2573% exceeds original 5% limit; Cloud fraction 21.7642% exceeds original 5% limit; Cloud fraction 18.9486% exceeds original 5% limit; Cloud fraction 23.2348% exceeds original 5% limit |
| Lower Mullamari | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 8.4836% exceeds original 5% limit; Cloud fraction 18.7435% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 99.9223% exceeds original 5% limit; Cloud fraction 29.4402% exceeds original 5% limit; Cloud fraction 17.8383% exceeds original 5% limit; Cloud fraction 16.1009% exceeds original 5% limit |
| Gundal | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 86.7093% exceeds original 5% limit; Cloud fraction 40.8940% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 9.0621% exceeds original 5% limit; Cloud fraction 39.9210% exceeds original 5% limit |
| Harinala | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 14.8957% exceeds original 5% limit; Cloud fraction 8.2176% exceeds original 5% limit; Cloud fraction 14.5863% exceeds original 5% limit; Cloud fraction 37.2392% exceeds original 5% limit; Cloud fraction 65.4588% exceeds original 5% limit; Cloud fraction 7.9107% exceeds original 5% limit; Cloud fraction 58.1446% exceeds original 5% limit; Cloud fraction 6.8117% exceeds original 5% limit |
| Hirehalla | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 11.7758% exceeds original 5% limit; Cloud fraction 9.9647% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 11.5258% exceeds original 5% limit; Cloud fraction 12.9497% exceeds original 5% limit; Cloud fraction 45.8975% exceeds original 5% limit; Cloud fraction 6.9184% exceeds original 5% limit; Cloud fraction 92.4689% exceeds original 5% limit |
| Uduthorehalla | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 18.1973% exceeds original 5% limit; Cloud fraction 6.5673% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Only 0.0000% of SCL water belongs to reservoir polygon; minimum 95%; Cloud fraction 80.5272% exceeds original 5% limit |
| Tattihalla | No approved CyFi input after 8 acquisitions checked in the 2026-06-25–2026-10-23 window. Cloud fraction 6.8174% exceeds original 5% limit; Cloud fraction 7.4060% exceeds original 5% limit; Cloud fraction 100.0000% exceeds original 5% limit; Cloud fraction 68.7602% exceeds original 5% limit; Cloud fraction 6.4110% exceeds original 5% limit; Cloud fraction 6.3593% exceeds original 5% limit |

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

Backend test output:

```text
........................................................................ [ 64%]
.......................................                                  [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/shriyahr/Documents/ChatGPT/Major/NEERWATCH/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
111 passed, 1 warning in 34.49s

```

Frontend build:

```text

> karnataka-bloom@1.0.0 build
> vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 17 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.57 kB │ gzip:   0.37 kB
dist/assets/index-DKtpgHCO.css   31.25 kB │ gzip:  10.65 kB
dist/assets/index-CLB_UiQA.js   400.64 kB │ gzip: 121.29 kB

✓ built in 94ms

```

Protected-file SHA256 checks: all 9 passed. Historical checkpoint/observation file size+mtime checks: all 16126 unchanged. The separate historical acquisition was not running at the initial process check; it was not restarted or interrupted.
Fresh browser verification was unavailable because local browser access was disabled. Current API and cached data were checked; earlier screenshots must not be described as visual verification of newly expanded estimates.

Remaining rejected inputs require different suitable acquisitions or a separately justified sampling methodology; QC must not be weakened solely to increase coverage. International pretrained model outputs cannot establish local accuracy without independent Karnataka field measurements. No prediction is a future FAI forecast, official alert, toxin estimate or laboratory result.
