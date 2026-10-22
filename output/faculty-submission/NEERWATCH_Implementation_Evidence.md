# NEERWATCH implementation evidence

Snapshot inspected: **22 October 2026**. Scope: existing empirical Sentinel-2 monitoring implementation. No operational source code, dataset or website was modified to prepare these deliverables. All authoring outputs are in this folder; temporary compiler tooling is outside the project.

## Verification and limitations

- 46 public registry entries; 92 latest/compatible-previous reservoir-date records audited.
- Every reported pixel estimate was independently recomputed from saved B04/B05 arrays using the implemented equation, compared with the persisted chlorophyll array on the saved validity mask, and the median checked within 1e-5 µg/L. Valid-pixel counts also matched.
- This is numerical reproduction from the same inputs, **not independent field validation**. No Karnataka field accuracy or ML performance is asserted.
- Full precision values, acquisition/source-scene identifiers and water-pixel counts: `verified-results.json`; paper rounds only presentation values.
- Existing verification logs: `../../../../work/scale-tests-final.log` (60 passed, one warning); `../../../../work/scale-build-final.log` (build successful). These prior logs were read, not presented as newly run tests.
- `../public-frontend-state-verification.json` records two interface-state sessions / 92 workspace loads. Prior report marks browser visual verification incomplete; this paper does not convert those checks into a visual verification claim.
- True-colour and heatmap figure panels reproduce actual cached PNG products; distribution figure uses actual stored reservoir polygons. No fabricated dashboard screenshot is used.
- Application retains legacy model-related endpoints/files and separately labelled Sentinel-3 archive context. Neither forms the active empirical concentration path, and neither supplies a result in this submission. Diagnostic NDCI/NDWI/FAI computations do not imply additional calibrated concentration outputs.
- No automatic daily scheduler, aquatic DSF/adjacency correction, local calibration, toxin inference, future forecasts or trained ML retrieval is claimed.

## Source traceability

Line numbers below refer to the inspected source snapshot; SHA-256 hashes make the references reproducible.

### `pipeline/satellite.py`

SHA-256: `65fcd5fa2edecb9e20f37b465b96faeecb60c9ddd91c5abda76e33bf3ea880bb`

- Lines 26–39: STAC pagination and dated search.
- Lines 42–105: Common grid, mosaic ownership, scale/offset, buffered masks and multiband validity.
- Lines 125–128: Fixed-stretch RGB generation.

### `pipeline/mosaic.py`

SHA-256: `5e27ba8e7416c52fafa6d3a8a12ca1f0301a93492e82a737db98c6fd6b3b5ade`

- Lines 6–25: Compatible same-pass grouping, footprint union and sorted observations.

### `pipeline/features.py`

SHA-256: `4ee42f249d4321e17b3608c9ab006e490208dddf58365c3b1ca3936f79d62cb6`

- Lines 6–36: Six bands, quality thresholds, spectral diagnostics; not trained concentration regression.

### `pipeline/sentinel2_chlorophyll.py`

SHA-256: `09b8c788f7b162b707e4d079ce3846aab73b357469bb69a145da163fcb2f2221`

- Lines 14–19: Named method, validation qualification, two workers and 60-day window.
- Lines 36–42: Exact Gilerson equation and rejection range.
- Lines 43–132: Newest-valid processing, footprint/QC, median, provenance, persisted products.
- Lines 133–141: Background requests, cached results and failure state.

### `backend/active.py`

SHA-256: `887feb65ae5d86be6e197982e34e5b19a052c0e285273299d85f3148ec6f60e0`

- Lines 6–15: Compatible previous acquisition, signed absolute/percentage change and categories.

### `backend/epa.py`

SHA-256: `be0705124ec3e817d594ba680cd82efb554ebde5578df0adee286e9f24640775`

- Lines 1–6: EPA source, thresholds, invalid-value handling.

### `backend/readiness.py`

SHA-256: `2d38327642482ccab909ed29a77139705d12313dda46daf3af8d66ec490cd7ad`

- Lines 8–44: Observation compatibility and publication gate.

### `backend/main.py`

SHA-256: `aed58a84392241ad0f900f771d74bf80ae2b9993d3f3e8131a186bd527ae78ca`

- Lines 15–54: List, CSV, process/status and scene-pinned media routes.
- Lines 68–76: Detail and boundary routes.
- Lines 84–90: PDF and built React serving.

### `backend/reports.py`

SHA-256: `2c8f6048209262b6e611d0cc18a147d8d0a198f9f39622db7ec48df7abd41211`

- Lines 18–56: ReportLab generation and actual image/history inclusion.

### `frontend/src/main.jsx`

SHA-256: `518cfda74a713b1b27c0abaa83bda72f9cd45a67cce542f2a48f27020eacf441`

- Lines 11–29: Leaflet boundaries, selection and popups.
- Lines 36–39: Category display.
- Lines 40–59: Requests, polling and refresh.
- Lines 60–75: Workspace, imagery, comparisons and PDF links.

## Storage and outputs

- `data/reservoirs.json`: published inventory (46), not all historical candidate directories.
- `data/boundaries/{id}.geojson`: source-attributed reservoir ROI.
- `data/sentinel2/{id}/latest.json` and `history.json`: observation values, dates and provenance.
- `{item_id}-bands.npz`: B02/B03/B04/B05/B08/B11 arrays, SCL and masks; composite records additionally retain tile ownership.
- Scene PNG RGB/heatmap and chlorophyll GeoTIFF: real cached outputs; TIFF carries georeferencing. The colour-bar PNG is not a georeferenced Leaflet overlay.
- `job.json`: processing state and errors, recovered on reload/restart.
- `backend/config.py`: file-based DATA paths; no operational database in this path.

## Authentic references

1. Gilerson et al., *Optics Express*, 18(23), 24109–24125, 2010, DOI: https://doi.org/10.1364/OE.18.024109. Authors/title/volume/issue/start page verified against publisher-deposited Crossref metadata. Page range corroborated by scholarly bibliographies. Direct publisher full text was inaccessible in this environment; no unverified experimental results from that paper are reproduced. The documented equation is verified directly against current Python and accessible published algorithm tables.
2. Assaf, Abdelal, Hussein, Halaweh and Alzubaidi, *Modeling Earth Systems and Environment*, 11, article 348, issue 5, 2025, DOI: https://doi.org/10.1007/s40808-025-02543-4. Full text examined at the co-author's institutional host: https://services.uop.edu.jo/InstructorProfile/files/Publication202571915713.pdf . Crossref verifies the same title/authors and article number. The paper's six regressors are related work only. No published performance value is attributed to NEERWATCH.
3. ESA SentiWiki Sentinel-2 Products: https://sentiwiki.copernicus.eu/web/s2-products . Provider L2A information; exact scaling and band metadata also retained in each project manifest.
4. Microsoft Planetary Computer collection: https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a . Source item URLs retained individually in results manifests.
5. EPA National Lakes Assessment 2022: https://nationallakesassessment.epa.gov/webreport/#trophic-state . Concentration bands match `backend/epa.py`; indicative transfer to Karnataka is qualified, not a local regulatory classification.
6. CWC National Register of Large Dams 2019: https://www.cwc.gov.in/sites/default/files/nrld-2019.pdf . Identity context; polygon source remains OpenStreetMap, not CWC.
7. OpenStreetMap attribution/license: https://www.openstreetmap.org/copyright . Boundary data © OpenStreetMap contributors, ODbL 1.0.
8. WaterQual: https://github.com/iliasmachairas/WaterQual . Current vendored index code is ancillary; the concentration expression is evaluated by NEERWATCH itself.

Access/inspection date: 22 October 2026. Crossref metadata snapshots are supplied in `reference-metadata/`.

## Full observation audit

Each row below is a real saved observation. Composite identifiers represent mosaics, not single source scenes; constituent identifiers and timestamps are retained in `verified-results.json`.

| Reservoir | Acquisition (UTC) | Scene / composite | Valid pixels | Median µg/L |
|---|---|---|---:|---:|
| krs | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFP_20261009T101803` | 7967 | 25.15317917 |
| krs | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927` | 17505 | 24.72256088 |
| bhadra | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PER_20261009T101803` | 22325 | 25.35454941 |
| bhadra | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 25065 | 23.97057533 |
| tungabhadra | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFS_20261012T091927` | 40407 | 27.33957291 |
| tungabhadra | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFS_20261017T102804` | 31965 | 42.19335175 |
| supa | 2026-10-10T05:27:31.025000Z | `S2C_MSIL2A_20261010T052731_R105_T43PDS_20261010T102100` | 18104 | 22.68390274 |
| supa | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 18533 | 25.31979561 |
| varahi | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PER_20261009T101803` | 1605 | 24.79433823 |
| varahi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 6269 | 22.86766243 |
| vani-vilasa | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFR_20261009T101803` | 7914 | 22.31194687 |
| vani-vilasa | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFR_20261012T091927` | 7950 | 21.65385437 |
| kabini | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFP_20261009T101803` | 3509 | 24.84024811 |
| kabini | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927` | 10417 | 23.84873962 |
| harangi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927` | 2357 | 24.56827164 |
| harangi | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PEP_20261017T102804` | 585 | 32.37010574 |
| hemavathi | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFQ_20261009T101803` | 2581 | 24.37245178 |
| hemavathi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFQ_20261012T091927` | 9897 | 24.26203346 |
| almatti | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QEU_20261009T101803` | 36206 | 24.49265099 |
| almatti | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QEU_20261012T091927` | 43831 | 20.98413277 |
| linganamakki | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PDR_20261009T101803` | 29646 | 24.36732292 |
| linganamakki | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927` | 35089 | 23.77728271 |
| markonahalli | 2026-10-14T05:07:51.025000Z | `S2C_MSIL2A_20261014T050751_R019_T43PFQ_20261014T100514` | 594 | 27.34554863 |
| markonahalli | 2026-10-19T05:08:19.024000Z | `S2B_MSIL2A_20261019T050819_R019_T43PFQ_20261019T085221` | 427 | 21.81388092 |
| yagachi | 2026-09-27T05:16:51.025000Z | `S2C_MSIL2A_20260927T051651_R062_T43PEQ_20260927T101415` | 1561 | 25.53193665 |
| yagachi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEQ_20261012T091927` | 506 | 25.22175980 |
| hidkal | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDT_20261015T090952` | 6594 | 21.73118401 |
| hidkal | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDT_20261020T101804` | 14343 | 20.39316750 |
| nugu | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFP_20261009T101803` | 854 | 25.66450310 |
| nugu | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFP_20261017T102804` | 1336 | 23.54079056 |
| kadra | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDS_20261015T090952` | 3736 | 27.52797318 |
| kadra | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 5347 | 24.67077637 |
| basava-sagara | 2026-10-12T05:17:39.024000Z | `MOSAIC_Sentinel2B_20261012T051739_62` | 25197 | 21.54588699 |
| basava-sagara | 2026-10-17T05:18:21.025000Z | `MOSAIC_Sentinel2C_20261017T051821_62` | 9586 | 29.17161179 |
| malaprabha | 2026-10-15T05:27:59.024000Z | `MOSAIC_Sentinel2B_20261015T052759_105` | 16517 | 23.27932739 |
| malaprabha | 2026-10-20T05:28:41.025000Z | `MOSAIC_Sentinel2C_20261020T052841_105` | 14213 | 22.69149399 |
| gerusoppa | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDR_20261015T090952` | 752 | 25.66936111 |
| gerusoppa | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDR_20261020T101804` | 739 | 24.47731781 |
| kodasalli | 2026-10-02T05:32:41.024000Z | `S2A_MSIL2A_20261002T053241_R105_T43PDS_20261002T101803` | 2171 | 20.37476921 |
| kodasalli | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 2008 | 19.61364365 |
| karanja | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 9119 | 17.98161125 |
| karanja | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 7741 | 20.29225540 |
| kanva | 2026-10-04T05:06:51.025000Z | `S2C_MSIL2A_20261004T050651_R019_T43PGQ_20261004T102617` | 374 | 20.87379456 |
| kanva | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGQ_20261009T090953` | 154 | 28.26469803 |
| manchanabele | 2026-10-14T05:07:51.025000Z | `S2C_MSIL2A_20261014T050751_R019_T43PGQ_20261014T100514` | 387 | 52.71988678 |
| manchanabele | 2026-10-19T05:08:19.024000Z | `S2B_MSIL2A_20261019T050819_R019_T43PGQ_20261019T085221` | 292 | 67.64892578 |
| suvarnavathy | 2026-09-29T05:06:49.024000Z | `S2B_MSIL2A_20260929T050649_R019_T43PGP_20260929T091314` | 171 | 31.06849670 |
| suvarnavathy | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGP_20261009T090953` | 271 | 31.52246475 |
| taraka | 2026-10-07T05:17:11.025000Z | `S2C_MSIL2A_20261007T051711_R062_T43PFP_20261007T100505` | 546 | 22.55152512 |
| taraka | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927` | 753 | 25.11584473 |
| votehole | 2026-09-27T05:16:51.025000Z | `S2C_MSIL2A_20260927T051651_R062_T43PEQ_20260927T101415` | 614 | 19.47901154 |
| votehole | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEQ_20261012T091927` | 579 | 24.60866547 |
| bennethora | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 2497 | 14.26628304 |
| bennethora | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 1777 | 21.77133560 |
| chandrampalli | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGV_20261009T101803` | 554 | 26.16268539 |
| chandrampalli | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 557 | 26.11521721 |
| dharma | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PDS_20261009T101803` | 756 | 16.53272629 |
| dharma | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDS_20261012T091927` | 465 | 17.82007980 |
| upper-tunga | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PER_20261009T101803` | 835 | 16.77939415 |
| upper-tunga | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 1635 | 16.18281174 |
| chikkahole | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGP_20261009T090953` | 79 | 30.03993416 |
| chikkahole | 2026-10-14T05:07:51.025000Z | `S2C_MSIL2A_20261014T050751_R019_T43PGP_20261014T100514` | 62 | 27.80917740 |
| chiklihole | 2026-10-07T05:17:11.025000Z | `S2C_MSIL2A_20261007T051711_R062_T43PEP_20261007T100505` | 27 | 25.42230415 |
| chiklihole | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927` | 45 | 27.21188354 |
| hattikuni | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGU_20261009T101803` | 120 | 29.67714882 |
| hattikuni | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGU_20261012T091927` | 113 | 27.04876328 |
| narihalla | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFS_20261009T101803` | 334 | 26.65930939 |
| narihalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFS_20261012T091927` | 326 | 24.00908279 |
| upper-mullamari | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 361 | 17.57335472 |
| upper-mullamari | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 351 | 23.27932739 |
| lower-mullamari | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGV_20261009T101803` | 517 | 19.42860985 |
| lower-mullamari | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 1011 | 17.45035934 |
| gundal | 2026-10-04T05:06:51.025000Z | `S2C_MSIL2A_20261004T050651_R019_T43PGP_20261004T102617` | 87 | 22.29980087 |
| gundal | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGP_20261009T090953` | 66 | 25.25246048 |
| gandorinala | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGV_20261009T101803` | 641 | 16.43280792 |
| gandorinala | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 698 | 17.08681488 |
| maskinala | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927` | 102 | 23.81313896 |
| maskinala | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFT_20261017T102804` | 106 | 25.90058136 |
| chulkinala | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 880 | 21.08140564 |
| chulkinala | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 656 | 20.38831329 |
| harinala | 2026-10-10T05:27:31.025000Z | `S2C_MSIL2A_20261010T052731_R105_T43PDT_20261010T102100` | 149 | 18.46661377 |
| harinala | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDT_20261015T090952` | 149 | 23.22782516 |
| hirehalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927` | 1431 | 20.70456505 |
| hirehalla | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFT_20261017T102804` | 1142 | 20.58097076 |
| uduthorehalla | 2026-09-09T05:06:49.024000Z | `S2B_MSIL2A_20260909T050649_R019_T43PGP_20260909T085145` | 76 | 39.58925629 |
| uduthorehalla | 2026-10-04T05:06:51.025000Z | `S2C_MSIL2A_20261004T050651_R019_T43PGP_20261004T102617` | 82 | 24.09103966 |
| jambhadhahalla | 2026-10-02T05:16:49.024000Z | `S2B_MSIL2A_20261002T051649_R062_T43PER_20261002T091946` | 140 | 21.34373474 |
| jambhadhahalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 236 | 24.97253036 |
| tattihalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDS_20261012T091927` | 1503 | 27.16395950 |
| tattihalla | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 1503 | 27.50455475 |
| savehaklu | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PDR_20261009T101803` | 286 | 25.23729897 |
| savehaklu | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927` | 719 | 23.27932739 |

## Document verification

Official IEEEtran conference class v1.8b and IEEEtran bibliography style compiled successfully with Tectonic. All seven research-paper pages and the architecture export were visually reviewed after rendering. Figures, equations, references and the complete 46-reservoir table are readable. Author and affiliation placeholders remain intentionally unfilled.
