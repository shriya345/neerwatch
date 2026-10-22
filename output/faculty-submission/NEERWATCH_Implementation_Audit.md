# NEERWATCH Implementation Audit

Audit date: **22 October 2026 (Asia/Kolkata)**. Repository: `/Users/shriyahr/Documents/ChatGPT/Major/NEERWATCH`.

## Verdict

**Do not submit both documents unchanged as a complete description of the CURRENT implemented backend.** The architecture is a sound simplified description of the **primary empirical Sentinel-2 chlorophyll workflow**, and the numerical results table is correct. The paper needs targeted corrections/qualifications before a strict accuracy sign-off: (1) it incorrectly treats legacy ML execution as outside the reservoir-detail call path; (2) it overstates per-observation metadata completeness for Varahi; (3) its numerical tolerance needs an explicit precision convention. Direct original full-text coefficient verification remains limited, and frontend image cropping is a real presentation limitation.

This is not evidence of fabricated chlorophyll concentrations. All 92 saved medians reproduce exactly at pipeline float32 precision; all 46 paper result rows match current data. No scientific accuracy is established without independent field measurements.

Classification counts: **{'VERIFIED': 46, 'PARTIALLY VERIFIED': 8, 'INCORRECT': 2}** across 56 claim rows. VERIFIED is scoped to the specific statement and test described, not blanket certification of the whole system.

## Documents actually audited

- `NEERWATCH_Current_Architecture.pdf` — 1 page(s), SHA-256 `b275c87d66895e356cfb48d5756a2b342013f585dec9fecd45a0affecd0f9d15`.
- `NEERWATCH_IEEE_Research_Paper.pdf` — 7 page(s), SHA-256 `de057bb9fee94fe03e487464296a081567fca40a1d0e467c9b33027e3f571de5`.

PDF text was extracted from the actual final PDFs; accompanying LaTeX was used only to inspect implementation/format and aid exact table matching. The existing implementation evidence file, reports, README statements and metadata labels were not accepted as proof by themselves.

## Method, safeguards and scope

- Established SHA-256 baselines for 1,487 existing source/data/model/submission files before testing. No protected file content changed. The only new repository deliverable is this audit Markdown; temporary scripts/logs live under `/tmp`.
- Ran a fresh Vite production build with output redirected to `/tmp/neerwatch-audit-vite-dist`, preserving the operational frontend/dist.
- Ran all backend tests with bytecode and pytest cache writes disabled, and temporary fixtures directed outside the project. Tests that emulate processing write only to pytest temporary directories. No live processing POST was submitted.
- Wrote an independent spectral audit outside the repository, using explicit NumPy expressions rather than importing `gilerson()`. Inspected all selected NPZ/JSON/GeoTIFF/PNG products and recomputed paired results. Independently reconstructed all possible SCL masks and polygon grids.
- Original localhost port **8010 was not listening**. Started the current app temporarily on **8011** with an in-memory read-only guard: POST/non-read methods blocked; processing-status reads served persisted job JSON without invoking recovery writes. Other tested GET routes execute the actual current app. This is an audit service, not a deployment change.
- Requested list/detail/boundary and generated ReportLab PDF for all 46 reservoirs; retrieved all three **previous-scene** media types for all 46; parsed CSV. The test suite additionally checks latest media and public/pending behavior.
- Executed current React source in two fresh jsdom sessions with write-free bundling and output redirected to `/tmp`: 92 workspace loads, 46 boundaries/table rows, popup/highlight/media selection, five sorts. CSS is omitted in that harness, so it is not visual proof.
- Separately used the real browser to inspect the built dashboard at 1280×720: overview, Bhadra statistics/RGB/heatmap toggle, Tungabhadra statistics/RGB. Did not click refresh/process. All-reservoir/mobile visual certification is not claimed.
- Read primary scientific/institutional sources. Reference access limitations are stated below rather than invented around.

### Status meanings

- **VERIFIED:** executing code and applicable inspected data/test support the scoped statement.
- **PARTIALLY VERIFIED:** mechanism exists but historical evidence, live exercise or scientific-source access is incomplete, or important qualification is needed.
- **UNVERIFIED:** available evidence cannot establish the claim.
- **INCORRECT:** current implementation/data contradict the wording. No code or document repair has been made.

## Claim-by-claim evidence table

Paths in source and data cells are relative to the repository root stated above, except `../work/`. Source ranges are inclusive one-based lines of the current inspected files. A data template means it was checked across the selected reservoir inventory, not just one example.

| ID | Document location | Claim | Exact implementing source | Stored data / API / reference | Read-only or safe verification | Status | Discrepancy / scope |
|---|---|---|---|---|---|---|---|
| A01 | Architecture 01; paper §VI | Sentinel-2 L2A via Planetary Computer STAC; six bands and SCL | pipeline/satellite.py:24–40,63–83; pipeline/features.py:6 | data/sentinel2/{id}/{item_id}.json: source_url, spectral_bands; matching NPZ | Inspected extraction code and all 92 NPZ files; fetched 12 original mosaic STAC items successfully. | VERIFIED | Acquisition implementation and cached outputs verified. This audit did not redownload every original raw spectral raster; it does not prove uninterrupted source-service availability. |
| A02 | Architecture 01; paper §V | Verified reservoir polygons and metadata from OpenStreetMap | backend/readiness.py:25–29; backend/monitoring.py:10–13 | data/reservoirs.json; data/boundaries/{id}.geojson; GET /api/reservoirs/{id}/boundary | All 46 public entries pass existing gate/tests; independently rerasterized every polygon against both saved grids. | VERIFIED | Verified means project geometry/location/provenance checks, not authoritative cadastral boundaries. Karnataka gate is a broad latitude/longitude box, not a Karnataka administrative-polygon containment test. |
| A03 | Architecture 02; paper §VIII-A | Newest valid observation within 60-day lookback; paginated newest-first search | pipeline/satellite.py:27–40; pipeline/sentinel2_chlorophyll.py:19,65–86 | Saved latest.json and attempts; tests/fixtures/krs-stac-scenes.json | Current source inspected; tests/test_processing_recovery.py:38–71 passes pagination/fallback fixtures. | PARTIALLY VERIFIED | Selection logic exists. No new 60-day acquisition search/processing was launched for all 46 because it would alter data. “Newest valid” is a selection policy, not freshly established freshness for every cached result. |
| A04 | Architecture 02; paper §VIII-A | Same-date/platform/orbit/baseline mosaics, timestamp separation ≤300 s | pipeline/mosaic.py:6–25; pipeline/satellite.py:55–60,77–88 | Basava Sagara and Malaprabha: four MOSAIC_ manifests, source_scenes and NPZ _tile_index | Read four mosaics; fetched all 12 constituent provider items; date/platform/orbit/baseline agree; ownership/coverage tests pass. | VERIFIED | These are four reservoir-date mosaics; constituent tile timestamps in each group agree (0 s separation). Basava lists four tiles but only three contribute polygon pixels; not four independent full-reservoir measurements. |
| A05 | Architecture 02; paper §VIII-B | Centroid-selected northern UTM projection and common 60 m analysis grid | pipeline/satellite.py:43–54; pipeline/sentinel2_chlorophyll.py:89,95 | 92 chlorophyll GeoTIFF CRS/transform/resolution; NPZ polygon_mask | Opened all 92 TIFFs: EPSG:32643, 60×60 m; reprojected/rasterized ROIs match saved masks. | VERIFIED | 60 m is analysis spacing; B04 native 10 m and B05 native 20 m are correctly distinguished in the paper. |
| A06 | Architecture 02; paper §VIII-B | Nearest-neighbour resampling through WarpedVRT; 1.5 million-cell limit | pipeline/satellite.py:50–54,75–76 | Source and analysis resolution metadata; persisted grid shapes | Read executing code; verified output grid geometry. | VERIFIED | Code confirms resampling method. Output pixels alone cannot prove which resampler was used historically without repeating raw-raster reads; this is implementation-level verification. |
| A07 | Architecture 02; paper §VIII-C | Reflectance = scale × DN + offset; zero DN missing; baseline-aware fallback | pipeline/satellite.py:80–83 | spectral_bands per observation; provider scene baseline; ESA product definition | 90/92 observations retain all six conversion metadata entries (scale 0.0001; offset −0.1; baselines 5.12/5.13). | PARTIALLY VERIFIED | Current code implements it; Varahi’s two manifests lack spectral_bands, so the universal statement that every saved manifest records scale/offset is false. Cached reflectance is already scaled; raw-DN conversion was not independently replayed for all 92. |
| A08 | Architecture 02; paper §VIII-D | Water = ROI ∩ SCL 6; one-pixel erosion; cloud/shadow 3/8/9/10 dilation | pipeline/features.py:19–26; pipeline/satellite.py:89,94–98 | NPZ _scl, polygon_mask, valid_mask for each record | Independently rebuilt masks with SciPy, six-band validity and algorithm range; 90 match exactly. | PARTIALLY VERIFIED | Varahi’s two NPZ files do not retain _scl. Their saved masks exist, but historical SCL/cloud/shore masking cannot be reproduced from those files. At 60 m the buffer is one morphology iteration, not an exact circular metric buffer. |
| A09 | Architecture 02; paper §VIII-D | All six reflectances finite, >0 and ≤1 | pipeline/features.py:24–31; pipeline/satellite.py:94–95 | Six-band NPZ arrays + valid_mask | Checked all 92 masks and arrays; full reconstruction possible for 90. | VERIFIED | This is conservative project screening, not an uncertainty guarantee; positive BOA is not proof of pure aquatic reflectance. |
| A10 | Paper §VIII-A | At least 95% scene footprint; mosaics also ≥95% data footprint | pipeline/sentinel2_chlorophyll.py:72–74; pipeline/mosaic.py:13,19–21; pipeline/satellite.py:87–88 | quality.footprint_fraction; mosaic quality.data_footprint_fraction; provider footprints | All four mosaic footprint fractions ≈1 and grid fraction 1.0; inspected gates and passing mosaic tests. | VERIFIED | Scene footprint uses Shapely areas in geographic coordinates; this is an approximate geometric ratio. The additional SCL data-footprint gate applies to mosaics, not every single-tile observation. |
| A11 | Architecture 03; paper §VIII-D,F | Minimum 25 pixels and 10% rasterized-polygon coverage, before and after estimation | pipeline/features.py:8–9,27–31; pipeline/satellite.py:89–90; pipeline/sentinel2_chlorophyll.py:87–90 | quality.algorithm_valid_pixels, algorithm_valid_fraction; NPZ masks | Independently counted all 92 masks and denominators; every selected record meets both gates. | VERIFIED | The 10% denominator is all ROI polygon cells. It does not mean ≥95% of the reservoir has a valid chlorophyll value. |
| A12 | Architecture 03; paper Eq. (2), §VIII-E | C=(35.75×B05/B04−19.30)^1.124 | pipeline/sentinel2_chlorophyll.py:39–44,87 | 92 B04/B05 arrays and persisted chlorophyll_a arrays | Independent float32 expression gives exact stored medians for all 92; float64 recalculation gives small roundoff differences. | VERIFIED | Coefficients/exponent and band order match exactly. Scientific transfer from aquatic reflectance to Sen2Cor BOA is explicitly experimental. |
| A13 | Architecture 03; paper §VIII-E | Positive inputs/base; finite results outside 1–100 µg/L rejected, not clipped | pipeline/sentinel2_chlorophyll.py:41–44,87–88 | chlorophyll_a NPZ/TIFF and valid_mask | Inspected conditional implementation, checked finite retained-pixel domain and masks; existing tests pass. | VERIFIED | 1–100 is a project acceptance rule, not a validated calibration interval. Invalid values are NaN; no boundary-value substitution is made. |
| A14 | Architecture 03; paper Eq. (3) | Reservoir aggregation is median of valid per-pixel concentrations | pipeline/sentinel2_chlorophyll.py:88–91 | Per-scene chlorophyll_a scalar, NPZ array/mask and TIFF | Recomputed all 92 medians without importing the pipeline estimator. | VERIFIED | It is a median of per-pixel estimates, not the equation evaluated on mean bands or an area-weighted whole-reservoir concentration. |
| A15 | Architecture 04; paper §VII,IX-A | Persistent JSON scene/latest/history/job state and compressed NPZ evidence | pipeline/sentinel2_chlorophyll.py:23–38,91–92,100–108; backend/config.py:19–27 | data/sentinel2/{id}/ latest.json, history.json, job.json, {item_id}.json, *-bands.npz | Read all 92 selected scene files and 46 history/latest pairs; masks and six arrays load successfully. | VERIFIED | Not a relational database. Older cached manifests are not automatically migrated to the newest metadata schema; see A07/A08/P10. |
| A16 | Architecture 04; paper §IX-A | Chlorophyll GeoTIFF is georeferenced with NaN nodata and provenance tags | pipeline/sentinel2_chlorophyll.py:94–95 | 92 *-chlorophyll.tif; GET /api/reservoirs/{id}/sentinel2/raster | Opened every TIFF, compared full arrays including NaNs to NPZ, checked grid/CRS and ROI. Previous-scene TIFFs served for all 46. | VERIFIED | The PNG heatmap is not the georeferenced raster. No georeferenced chlorophyll Leaflet overlay is implemented or claimed in the paper. |
| A17 | Architecture 04/06; paper §IX-A,C | True-colour PNG uses B04/B03/B02, fixed /0.25 display stretch | pipeline/satellite.py:123–128; pipeline/sentinel2_chlorophyll.py:90 | 92 *-rgb.png and underlying NPZ; frontend media view | Decoded all RGB PNGs and compared bytes with independently reconstructed RGB arrays: 92/92 exact. | VERIFIED | Display stretch is not used in the chlorophyll equation. save_rgb receives mask but does not apply a reservoir crop to the RGB; surrounding scene context remains visible. |
| A18 | Architecture 04/06; paper §IX-A,C, Fig.3 | PNG chlorophyll maps use viridis, 1–100 µg/L colour scale | pipeline/sentinel2_chlorophyll.py:96–99; frontend/src/main.jsx:66,71 | 92 *-chlorophyll.png; paper figures/satellite-products.png | All PNGs decode; code establishes plotting scale; browser heatmap toggle inspected for Bhadra. | VERIFIED | Stored full PNG products are readable; dashboard object-fit:cover crops the visible full map/colour bar in the inspected viewport (see F06). |
| A19 | Architecture 05; paper §VIII-G | EPA trophic bands ≤2, >2–7, >7–30, >30 µg/L; no invalid category | backend/epa.py:1–6; frontend/src/main.jsx:36–38 | GET /api/reservoirs classification; EPA National Lakes Assessment trophic-state benchmarks | Independently classified all 46 latest values; boundary/invalid tests pass; official EPA page confirms bands. | VERIFIED | Appropriately qualified as satellite-derived screening; no WHO dominance rule is used for this EPA trophic category. |
| A20 | Architecture 05; paper §VIII-H, Eqs.(4–5) | Earlier different-calendar-date compatible observation; signed absolute and percent change | backend/active.py:6–15; backend/readiness.py:8–10 | latest.json/history.json; API monitoring.change | Independently selected previous observations and recalculated all 46 deltas and percentages; API/CSV values match. | VERIFIED | Compatibility compares configured method/correction/QC metadata, not identical pixel footprints or validated biological comparability. |
| A21 | Architecture 05; paper §IX-B | FastAPI list, detail and boundary services, React static serving | backend/main.py:11–24,68–76,88–90 | GET /api/reservoirs; /api/reservoirs/{id}; /boundary; / | All 46 list/detail/boundary GETs worked on isolated read-only server using current application. | VERIFIED | Original port 8010 was not listening at audit start. Successful checks used temporary 8011; this proves current app behavior, not that 8010 was online. |
| A22 | Architecture 05/06; paper §IX-B,C | Comparison CSV contains dated concentrations, changes, categories and links | backend/main.py:25–33; frontend/src/main.jsx:69 | GET /api/chlorophyll-review.csv | Parsed 46 exported rows; full-precision latest concentrations and percentage changes exactly match current disk calculations. | VERIFIED | CSV image URLs point to latest media and omit scene_id; frontend comparison URLs are scene-pinned. Do not describe the CSV links as immutable historical links. |
| A23 | Architecture 05; paper §IX-B | Scene-pinned RGB/heatmap/GeoTIFF endpoints | backend/main.py:44–54; frontend/src/main.jsx:66,69,71 | GET /api/reservoirs/{id}/sentinel2/{kind}?scene_id=... | Retrieved previous-acquisition RGB/heatmap/TIFF for all 46; existing test verifies bytes against selected PNG and 404 for unknown ID. | VERIFIED | A saved scene ID selects history; original scene asset must still exist. All selected pairs currently have required products. |
| A24 | Architecture 05; paper §IX-B | POST starts background processing; GET polls status; two workers; explicit failures | backend/main.py:34–43; pipeline/sentinel2_chlorophyll.py:17,23–38,119–138; frontend/src/main.jsx:49–61 | POST /api/reservoirs/{id}/process-sentinel2; GET .../processing; job.json | Read actual call chain; temporary-directory tests exercise queue/failure/interruption/fallback. Did not submit real production processing POSTs. | PARTIALLY VERIFIED | Real current end-to-end manual reacquisition was not re-executed because user prohibited dataset changes. No fresh all-reservoir processing-success claim is justified by this audit. |
| A25 | Paper §IX-A | Restart/load recovery and cached reuse | pipeline/sentinel2_chlorophyll.py:23–34,76–83,123–127 | Persisted job/latest/scene JSON | Tests/test_processing_recovery.py:15–36 verifies persisted state and interrupted jobs under temporary storage. | VERIFIED | Recovery marks interrupted work failed for retry; it does not automatically resume the interrupted raster computation. Cached reuse checks method/resolution/products, not every provenance/QC field. |
| A26 | Architecture 05/06; paper §IX-C | ReportLab creates dated per-reservoir PDF with values, imagery, history and limitations | backend/reports.py:18–56; backend/main.py:84–87; frontend/src/main.jsx:70 | GET /api/reservoirs/{id}/report.pdf | Requested and parsed all 46 generated PDFs; reservoir names and readable pages present; production dataset unchanged. | VERIFIED | PDF generation is backend-side. This is distinct from the academic IEEE paper PDF. |
| F01 | Architecture 06; paper §IX-C | React dashboard, Leaflet map and reservoir boundary selection/highlight | frontend/src/main.jsx:1–5,11–27,57,68 | GET boundary route; Leaflet SVG paths and popups | Ran current JSX in two fresh DOM sessions: 46 boundary paths, 46 comparison rows, 92 selected workspace/popup/highlight checks; browser overview visibly rendered. | VERIFIED | DOM tests establish behavior, not cartographic correctness or every screen-size layout. Project boundaries are not field-surveyed shorelines. |
| F02 | Architecture 06; paper §IX-C | Dated statistics and synchronized true-colour/heatmap views | frontend/src/main.jsx:44–61,66,70–73 | Reservoir detail API; scene-pinned media URL | 92 DOM workspace loads matched source concentrations; browser Bhadra showed 23.97, 12 Oct, Eutrophic, −5.5%; Tungabhadra 42.19, 17 Oct, Hypereutrophic, +54.3%. | VERIFIED | Summary cards round percent to one decimal; paper uses two. This is display rounding, not inconsistent data. |
| F03 | Architecture 06; paper §IX-C | Comparison table, source links, region, signed change, previews, five sort modes | frontend/src/main.jsx:64–65,69 | 46 comparison rows; CSV/media routes | 92 DOM checks and five sort modes passed twice; exact source inspected. | VERIFIED | Region/location fields are project metadata, sometimes generic Karnataka; not independently verified district administration boundaries. |
| F04 | Paper §X-C | Saved interface audit reports 92 loads across two sessions; historical browser visual verification incomplete | frontend/src/main.jsx:11–74; ../work/frontend-check/check.mjs:1–47 | output/public-frontend-state-verification.json; fresh temporary audit DOM results | Re-executed harness with output redirected to /tmp and CSS-free bundle; 92 loads passed. Separately inspected real browser overview/Bhadra/Tungabhadra screenshots. | VERIFIED | Historical “visual incomplete” wording is fair for original check. Current audit adds sample desktop visual checks; all 46 layouts and responsive/mobile states are still not visually certified. |
| F05 | Paper §IX-B | Public inventory gate requires two compatible observations, provenance and files | backend/readiness.py:8–44; backend/monitoring.py:10–13 | Public data/reservoirs.json; internal pending-reservoirs.json | Existing public-readiness and pending-inaccessibility tests pass. Current public API count is 46. | VERIFIED | Gate checks metadata/file existence; it does not independently recompute spectra, require retained SCL, verify scaling metadata, or establish scientific accuracy. |
| F06 | Frontend presentation quality, adjacent to architecture 06 | Full heatmap and colour-bar visibility in dashboard | frontend/src/style.css:2 (.reservoir-photo); frontend/src/main.jsx:71 | Bhadra stored heatmap vs browser image view | Read CSS (height 210px; object-fit:cover); inspected Bhadra heatmap at 1280×720 viewport. | PARTIALLY VERIFIED | Image toggles and map rendering work, but viewport crops the full heatmap/colour scale. This is a real UI limitation; paper uses full stored products and does not explicitly promise uncropped dashboard maps. |
| P01 | Abstract; paper §V,X-A; Table I | 46 operational reservoirs and 92 compatible reservoir-date observations | backend/monitoring.py:10–13; backend/active.py:6–15; backend/readiness.py:8–44; tests/test_scale_publication.py:6–16 | 46 public registry entries; 46 history files, each with two records | Counted registry/public response/paired histories independently; all 46 have eligible previous/latest records. | VERIFIED | 92 is reservoir-date aggregates, not 92 independent satellite scenes. There are 56 unique scene/composite item IDs across these records; some scenes are shared by reservoirs. |
| P02 | Abstract; paper §X-A | Latest estimate range 16.18–67.65 µg/L | pipeline/sentinel2_chlorophyll.py:91; backend/active.py:12–15 | Latest medians for all 46 | Independent minimum 16.182811737060547 (Upper Tunga), maximum 67.64892578125 (Manchanabele). | VERIFIED | Rounded numbers match. They are experimental empirical estimates, not measured field concentrations. |
| P03 | Abstract; paper §X-A | 42 eutrophic, four hypereutrophic; zero oligotrophic/mesotrophic | backend/epa.py:3–6 | 46 latest medians and independent classification | Counted 42 E and 4 H; H sites are Tungabhadra, Harangi, Manchanabele, Suvarnavathy. | VERIFIED | Not a statistically representative statewide trophic survey; paper correctly states this limitation. |
| P04 | Paper §X-A | 20 increasing, 26 decreasing; paired dates 9 Sep–20 Oct 2026 | backend/active.py:11–15 | All 46 previous/latest pairs | Independent signs and min/max acquisition dates agree. | VERIFIED | Maximum date is the newest date within accepted pairs, not a claim that no later imagery exists. |
| P05 | Paper §X-A | Latest algorithm-valid coverage 11.60%–81.91% | pipeline/sentinel2_chlorophyll.py:88–91 | All latest valid_mask and polygon_mask arrays | Recomputed extrema 0.11599297012302284 and 0.819131924614506. | VERIFIED | Coverage is retained pixel support, not percentage scientific accuracy. |
| P06 | Paper §X-B and Table I | Every tabulated reservoir name, date, C, delta, percentage and category | backend/active.py:6–15; backend/epa.py:3–6 | Current JSON/NPZ and actual final IEEE PDF Table I (page 7) | Compared all 46 complete row strings after PDF whitespace normalization, plus LaTeX table values: zero mismatches. | VERIFIED | Four initial extraction matches differed only in PDF kerning whitespace (e.g., V arahi); normalized text and rendered table contain correct values. No data discrepancy. |
| P07 | Paper §X-A, conclusion | Independent numerical reproduction of all 92 estimates | pipeline/sentinel2_chlorophyll.py:39–44,87–95; scripts/verify_live_processing.py:24–43 | Actual saved spectral arrays, masks, NPZ chlorophyll, TIFF, scalars | This audit used a separately written NumPy expression, did not call gilerson(), and compared all 92. Float32 median error is exactly zero; float64 maximum median error is 1.779271656232595e−5 µg/L. | VERIFIED | Numerical consistency is verified. Neither this audit nor an earlier script supplies independently measured chlorophyll ground truth or independent atmospheric-correction validation. |
| P08 | Paper §X-A, page 5 | Medians agreed within 1e−5 µg/L numerical tolerance | pipeline/sentinel2_chlorophyll.py:42–44 (float32 output); scripts/verify_live_processing.py:25–29 (float64, relative rtol=2e−5) | Manchanabele latest, 19 Oct 2026; stored 67.64892578125 | Independent float32 expression reproduces exactly; independent float64 median is 67.64894357396656, absolute difference 1.77927e−5. | PARTIALLY VERIFIED | True for same-float32 reproduction, but not a precision-independent absolute bound. Specify dtype and absolute/relative tolerance; existing verification script uses relative tolerance, not the paper’s blanket absolute bound. |
| P09 | Paper §X-C | 60 passing backend tests and successful frontend build | tests/*.py; frontend/package.json:1 (build); frontend/dist/index.html:1 | Fresh isolated pytest log; existing frontend/dist assets | Reran full suite: 60 passed, 1 Starlette deprecation warning, 27.28 s. Separately ran the actual Vite production build with output redirected to /tmp; it succeeded. | VERIFIED | Actual production build was rerun safely with --outDir /tmp/neerwatch-audit-vite-dist; project frontend/dist was not overwritten. Passing tests are software checks and include temporary/mock fixtures, not 60 scientific validations. |
| P10 | Paper §VI, page 2 | Each saved manifest records spectral assets, scale/offset and CRS | pipeline/satellite.py:80–83,103; pipeline/sentinel2_chlorophyll.py:91 | Varahi two selected per-scene/latest/history manifests | Inspected all 92 spectral_bands maps; 90 complete, Varahi two lack the entire spectral_bands field. | INCORRECT | Blanket “each saved manifest” overstates current cached schema coverage. Narrow to current writer/90 complete observations and disclose the two historical provenance gaps, or repair later with verified originals. |
| P11 | Paper §III, page 1; scope implications in abstract/conclusion | Historical training files are outside the active monitoring path | backend/monitoring.py:15–47,68–80,102–118; backend/main.py:68–70; pipeline/train.py:20 onward | models/metadata.json and model files; reservoir detail prediction/model fields | Current GET detail responses report model trained for all 46 and research_estimate severity for 12; legacy_summary calls predict before Sentinel-2 primary fields override. | INCORRECT | ML is excluded from displayed chlorophyll concentration/EPA/change calculations, but not from the complete reservoir-detail execution path. The paper must state that narrower scope. No claim is made here that the legacy classifier is scientifically valid. |
| P12 | Abstract/conclusion; equation pathway | Primary Sentinel-2 chlorophyll, categories and trends do not use trained ML or forecasting | pipeline/sentinel2_chlorophyll.py:39–44,87–91; backend/active.py:6–15; backend/monitoring.py:114–118 | Primary sentinel2 payload and React statistics | Traced numeric data flow to fixed equation; all primary results reproduce without models; frontend reads data.sentinel2. | VERIFIED | This scoped claim is correct. A broader claim that the repository/backend contains or executes no trained ML is incorrect (P11). |
| P13 | Paper §VI,IX-B; Fig.3 | Sentinel-3 archive not substituted for primary Sentinel-2 concentration | backend/monitoring.py:114–118; backend/active.py:6–15; frontend/src/main.jsx:66,74 | Primary sentinel2 vs separately labelled sentinel3_comparison response | Primary data matches B04/B05 exactly; source code keeps comparison in separate field/details panel. | VERIFIED | Legacy fields remain in API; paper may scope them out but should not imply complete backend removal. |
| P14 | Paper §XI; architecture footer | No independent Karnataka field validation, aquatic DSF/adjacency correction, toxin/dominance determination or forecast in primary path | pipeline/sentinel2_chlorophyll.py:15–16,91; backend/active.py:6–15; frontend/src/main.jsx:73 | Processing manifests, model metadata karnataka_field_validated=false, absence of matched local validation in documented path | Inspected estimator inputs, output schema and active call chain. No primary future horizon, toxin or dominance estimator is invoked. | VERIFIED | A repository inspection cannot prove no external field study exists; it establishes that none validates the current results in this implementation. Local absence is the supported statement. |
| P15 | Paper §VII,XI | File-based storage; manual refresh; no continuously scheduled acquisition service | backend/config.py:5–8,19–27; pipeline/sentinel2_chlorophyll.py:119–138; frontend/src/main.jsx:58–61 | Filesystem cache, FastAPI process route | Inspected current processing modules and scheduling references; no acquisition scheduler in active app. | VERIFIED | Torch learning-rate scheduler in legacy training is unrelated to acquisition scheduling. This does not audit external user cron/automation settings. |
| P16 | Paper Fig.1 and Fig.3 | Real reservoir geometries and cached satellite products are used as figures | pipeline/satellite.py:123–128; pipeline/sentinel2_chlorophyll.py:94–99 | figures/reservoir-distribution.pdf; figures/satellite-products.png; KRS/Basava source PNGs | Verified current source PNG reconstruction and decoded products; compared figure labels/dates with selected scenes; map points correspond to registry/polygons. | VERIFIED | These are real project-derived figures, not field measurements or UI screenshots. The academic figure is a composed plate, not a raw satellite sensor image unchanged. |
| P17 | Paper format and references | Official IEEEtran conference layout, equations, bibliography and placeholders | output/faculty-submission/NEERWATCH_IEEE_Research_Paper.tex:1–9; NEERWATCH_References.bib | Actual seven-page PDF and LaTeX source | PDF opens and extracts; source uses IEEEtran conference class and IEEEtran bibliography style; two-column body with full-width figures/table. | VERIFIED | Author and affiliation placeholders prevent final submission readiness. Formatting is not a claim of IEEE acceptance or compliance with a particular conference page limit. |
| R01 | Paper [1], §II-A/III | Gilerson 2010 supports red/NIR two-band chlorophyll retrieval | pipeline/sentinel2_chlorophyll.py:14,39–44 | DOI 10.1364/OE.18.024109; institutional publication record and PubMed | Authors, title, year, journal, 18(23), 24109–24125 verified; author institutional abstract states MERIS aquatic-reflectance ratios. | VERIFIED | Reference supports empirical red/NIR basis. It does not validate this Sentinel-2 BOA adaptation, 60 m grid, masks or Karnataka results. |
| R02 | Paper [1], Eq.(2) attribution | Exact 35.75, −19.30, 1.124 coefficients are Gilerson-derived | pipeline/sentinel2_chlorophyll.py:39–44 | Original institutional abstract; accessible De Keukelaere et al. 2023, Remote Sensing 15,1345, p.5 Eq.(9), cites Gilerson | Exact expression corroborated in a primary research publication. Original 2010 full PDF blocked (403) in this environment. | PARTIALLY VERIFIED | Original bibliographic/ratio basis is verified; direct original full-text coefficient verification remains inaccessible. Add the accessible implementation/transfer citation for precise traceability; do not claim a direct full-text inspection of Gilerson. |
| R03 | Paper [2], §II-B/III | Assaf et al. 2025 uses Sentinel-2/in-situ data and six supervised regressors with feature importance | Not a NEERWATCH implementation claim; cf. pipeline/sentinel2_chlorophyll.py:39–44 | DOI 10.1007/s40808-025-02543-4; author institution PDF, p.1 abstract | Downloaded/read full 26-page publication; five authors/title/year/vol.11/article348 and six named regressors agree. | VERIFIED | No published scores are attributed to NEERWATCH. Bibliography “p.348 ... article348” is redundant: 348 is article number, not a conventional page number. |
| R04 | Paper [6] and §VI/VIII-C | ESA supports provider L2A BOA, resolution distinctions and metadata-dependent offsets | pipeline/satellite.py:75–83 | Official SentiWiki S2 Products, Level-2A section | Primary guidance confirms zero DN no-data and (DN+BOA_ADD_OFFSET)/QUANTIFICATION_VALUE from PB04.00. | VERIFIED | Metadata-based correction is scientifically supported; −0.1 fallback is a project implementation decision, not a universal ESA constant for every possible product. |
| R05 | Paper [8], §VIII-G | EPA source supports 2/7/30 concentration bands | backend/epa.py:2–6 | Official NLA2022 trophic-state benchmarks | Official page directly lists ≤2, >2–7, >7–30, >30 ppb. | VERIFIED | Numerically used as µg/L for freshwater. Supports reference bands, not Karnataka regulation or retrieval accuracy. |
| R06 | Paper [3], §III | WaterQual supplies ancillary NDCI, not the primary concentration coefficients | pipeline/sentinel2_chlorophyll.py:12,87; vendor/waterqual/indices.py:67–81 | Vendored index implementation/license; GitHub WaterQual upstream | Actual import/call traced; main concentration uses own gilerson() instead of upstream placeholder coefficients. | VERIFIED | Repository is software provenance, not peer-reviewed validation of the displayed concentrations. |
| R07 | Paper [4]/[5]/[7], §V–VI | CWC supplies identity context; OSM supplies polygons/licensing; Planetary Computer supplies catalog/assets | backend/readiness.py:25–29; pipeline/satellite.py:24,31,68–83 | Registry identity_verification and osm_url; source URLs in manifests; official CWC PDF in work folder | Inspected stored identity records and official source register; successfully fetched 12 provider STAC records. | PARTIALLY VERIFIED | The register supports dam identities; not all 46 polygons were independently rematched to the authoritative register during this audit. OSM provenance/location tests do not make shorelines authoritative. |

## Findings requiring attention before submission

### 1. Legacy ML is still executed by reservoir-detail requests

Paper §III says historical training-related files are outside the active monitoring path. That is too broad. `backend/main.py:68–70` calls `summary`; `backend/monitoring.py:114–118` first calls `legacy_summary`, whose lines 80 and 102–108 invoke prediction logic. `predict` at lines 36–47 loads and evaluates the MLP and Random Forest when applicable. Model artifacts exist and the runtime metadata status is `trained`.

Fresh actual detail responses contain `prediction.status = research_estimate` and a severity for **12/46 reservoirs**: KRS, Bhadra, Tungabhadra, Supa, Varahi, Vani Vilasa Sagara, Kabini, Harangi, Hemavathi, Almatti, Linganamakki and Basava Sagara. The other 34 return unavailable predictions but still expose model status. These are legacy research categories, not chlorophyll-a regressions or validated Karnataka results.

The primary `sentinel2` concentrations, trophic categories and temporal changes are independent of those models. The diagram remains accurate **as a primary workflow diagram**, but not as an exhaustive inventory of everything executed in the backend. Recommended wording (not applied): “The primary chlorophyll-a workflow uses no trained ML. The detail API retains a separate legacy severity-classification branch which does not feed these chlorophyll results or the primary dashboard statistics.”

### 2. Varahi prevents blanket provenance and historical-mask claims

Both selected Varahi records (9 and 12 October 2026) have six spectral arrays, saved valid/polygon masks, readable RGB/heatmap/TIFF, and reproducible medians. However:

- `spectral_bands` is absent from the manifests: no per-band source-asset/scale/offset/CRS metadata block.
- `_scl` is absent from both NPZ files: the original cloud/shore/water decisions cannot be independently rebuilt from those retained files.

The current writer records these items, but the cached older products were not upgraded. Therefore the paper's universal per-manifest wording is inaccurate, and a universal proof of historical SCL processing is unavailable. Explicitly distinguish current writer behavior, 90 complete retained records, and two provenance-limited historical records. Do not infer missing metadata from neighboring reservoirs.

### 3. Numerical agreement needs a dtype/tolerance qualifier

At **float32**, a separately written expression reproduces all 92 medians with maximum absolute error **0.0 µg/L**. At **float64**, all estimates remain consistent to small roundoff: maximum per-pixel absolute difference **2.9386792263608186e−5 µg/L**, maximum median absolute difference **1.779271656232595e−5 µg/L**. The latter occurs at Manchanabele, 19 October: stored 67.64892578125 versus independently recalculated 67.64894357396656.

Thus “within 1e−5 µg/L” is true for the same-float32 audit, but is not a precision-independent absolute statement. Existing `scripts/verify_live_processing.py:25–29` explicitly casts to float64 and uses **relative** tolerance 2e−5. State precision and tolerance type. These errors do not change any published two-decimal table value, trophic category or trend. Independent arithmetic reproduction is not independent ground truth.

### 4. Frontend behavior is stronger than the original visual evidence, but not flawless

Fresh DOM verification passed 92 selected workspaces across two sessions. Real browser sample checks now confirm visible Bhadra and Tungabhadra values and actual image switching. However `.reservoir-photo` in `frontend/src/style.css:2` uses fixed 210 px height with `object-fit:cover`. Bhadra's displayed heatmap/colour bar is visibly cropped. The full stored PNG and paper figure are unaffected. Do not claim full-image visibility or all-device visual validation. Original port 8010 being offline is also distinct from a functioning isolated current-code audit instance.

### 5. Source support and scientific limits

The references support an empirical red/NIR retrieval basis and EPA reference concentration categories; they do not scientifically validate NEERWATCH's BOA approximation or Karnataka estimates. The paper mostly makes this distinction correctly. The original Gilerson full PDF was inaccessible; exact coefficients are corroborated by an accessible primary later publication and current code, rather than claimed to have been read directly in the original full text. Author/affiliation placeholders still need filling before actual submission. Assaf bibliography entry uses both “p. 348” and “article 348”; 348 is an article number, a minor bibliographic formatting issue.

## Numerical results checked against current stored data

The following values were recomputed from current selected JSON and spectral arrays, not copied from an earlier report. Both concentrations and all changes/categories match the actual PDF's complete table after display rounding.

| Reservoir | Earlier acquisition | Latest acquisition | Earlier µg/L | Latest µg/L | Δ µg/L | Change % | Category | PDF match |
|---|---|---|---:|---:|---:|---:|---|---|
| KRS | 2026-10-09 | 2026-10-12 | 25.15 | 24.72 | -0.43 | -1.71 | Eutrophic | VERIFIED |
| Bhadra | 2026-10-09 | 2026-10-12 | 25.35 | 23.97 | -1.38 | -5.46 | Eutrophic | VERIFIED |
| Tungabhadra | 2026-10-12 | 2026-10-17 | 27.34 | 42.19 | +14.85 | +54.33 | Hypereutrophic | VERIFIED |
| Supa | 2026-10-10 | 2026-10-20 | 22.68 | 25.32 | +2.64 | +11.62 | Eutrophic | VERIFIED |
| Varahi | 2026-10-09 | 2026-10-12 | 24.79 | 22.87 | -1.93 | -7.77 | Eutrophic | VERIFIED |
| Vani Vilasa Sagara | 2026-10-09 | 2026-10-12 | 22.31 | 21.65 | -0.66 | -2.95 | Eutrophic | VERIFIED |
| Kabini | 2026-10-09 | 2026-10-12 | 24.84 | 23.85 | -0.99 | -3.99 | Eutrophic | VERIFIED |
| Harangi | 2026-10-12 | 2026-10-17 | 24.57 | 32.37 | +7.80 | +31.76 | Hypereutrophic | VERIFIED |
| Hemavathi | 2026-10-09 | 2026-10-12 | 24.37 | 24.26 | -0.11 | -0.45 | Eutrophic | VERIFIED |
| Almatti | 2026-10-09 | 2026-10-12 | 24.49 | 20.98 | -3.51 | -14.32 | Eutrophic | VERIFIED |
| Linganamakki | 2026-10-09 | 2026-10-12 | 24.37 | 23.78 | -0.59 | -2.42 | Eutrophic | VERIFIED |
| Markonahalli | 2026-10-14 | 2026-10-19 | 27.35 | 21.81 | -5.53 | -20.23 | Eutrophic | VERIFIED |
| Yagachi | 2026-09-27 | 2026-10-12 | 25.53 | 25.22 | -0.31 | -1.21 | Eutrophic | VERIFIED |
| Hidkal | 2026-10-15 | 2026-10-20 | 21.73 | 20.39 | -1.34 | -6.16 | Eutrophic | VERIFIED |
| Nugu | 2026-10-09 | 2026-10-17 | 25.66 | 23.54 | -2.12 | -8.27 | Eutrophic | VERIFIED |
| Kadra | 2026-10-15 | 2026-10-20 | 27.53 | 24.67 | -2.86 | -10.38 | Eutrophic | VERIFIED |
| Basava Sagara | 2026-10-12 | 2026-10-17 | 21.55 | 29.17 | +7.63 | +35.39 | Eutrophic | VERIFIED |
| Malaprabha (Renuka Sagara) | 2026-10-15 | 2026-10-20 | 23.28 | 22.69 | -0.59 | -2.53 | Eutrophic | VERIFIED |
| Gerusoppa | 2026-10-15 | 2026-10-20 | 25.67 | 24.48 | -1.19 | -4.64 | Eutrophic | VERIFIED |
| Kodasalli | 2026-10-02 | 2026-10-20 | 20.37 | 19.61 | -0.76 | -3.74 | Eutrophic | VERIFIED |
| Karanja | 2026-10-12 | 2026-10-17 | 17.98 | 20.29 | +2.31 | +12.85 | Eutrophic | VERIFIED |
| Kanva | 2026-10-04 | 2026-10-09 | 20.87 | 28.26 | +7.39 | +35.41 | Eutrophic | VERIFIED |
| Manchanabele | 2026-10-14 | 2026-10-19 | 52.72 | 67.65 | +14.93 | +28.32 | Hypereutrophic | VERIFIED |
| Suvarnavathy | 2026-09-29 | 2026-10-09 | 31.07 | 31.52 | +0.45 | +1.46 | Hypereutrophic | VERIFIED |
| Taraka | 2026-10-07 | 2026-10-12 | 22.55 | 25.12 | +2.56 | +11.37 | Eutrophic | VERIFIED |
| Votehole | 2026-09-27 | 2026-10-12 | 19.48 | 24.61 | +5.13 | +26.33 | Eutrophic | VERIFIED |
| Bennethora | 2026-10-12 | 2026-10-17 | 14.27 | 21.77 | +7.51 | +52.61 | Eutrophic | VERIFIED |
| Chandrampalli | 2026-10-09 | 2026-10-12 | 26.16 | 26.12 | -0.05 | -0.18 | Eutrophic | VERIFIED |
| Dharma | 2026-10-09 | 2026-10-12 | 16.53 | 17.82 | +1.29 | +7.79 | Eutrophic | VERIFIED |
| Upper Tunga | 2026-10-09 | 2026-10-12 | 16.78 | 16.18 | -0.60 | -3.56 | Eutrophic | VERIFIED |
| Chikkahole | 2026-10-09 | 2026-10-14 | 30.04 | 27.81 | -2.23 | -7.43 | Eutrophic | VERIFIED |
| Chiklihole | 2026-10-07 | 2026-10-12 | 25.42 | 27.21 | +1.79 | +7.04 | Eutrophic | VERIFIED |
| Hattikuni | 2026-10-09 | 2026-10-12 | 29.68 | 27.05 | -2.63 | -8.86 | Eutrophic | VERIFIED |
| Narihalla | 2026-10-09 | 2026-10-12 | 26.66 | 24.01 | -2.65 | -9.94 | Eutrophic | VERIFIED |
| Upper Mullamari | 2026-10-12 | 2026-10-17 | 17.57 | 23.28 | +5.71 | +32.47 | Eutrophic | VERIFIED |
| Lower Mullamari | 2026-10-09 | 2026-10-12 | 19.43 | 17.45 | -1.98 | -10.18 | Eutrophic | VERIFIED |
| Gundal | 2026-10-04 | 2026-10-09 | 22.30 | 25.25 | +2.95 | +13.24 | Eutrophic | VERIFIED |
| Gandorinala | 2026-10-09 | 2026-10-12 | 16.43 | 17.09 | +0.65 | +3.98 | Eutrophic | VERIFIED |
| Maskinala | 2026-10-12 | 2026-10-17 | 23.81 | 25.90 | +2.09 | +8.77 | Eutrophic | VERIFIED |
| Chulkinala | 2026-10-12 | 2026-10-17 | 21.08 | 20.39 | -0.69 | -3.29 | Eutrophic | VERIFIED |
| Harinala | 2026-10-10 | 2026-10-15 | 18.47 | 23.23 | +4.76 | +25.78 | Eutrophic | VERIFIED |
| Hirehalla | 2026-10-12 | 2026-10-17 | 20.70 | 20.58 | -0.12 | -0.60 | Eutrophic | VERIFIED |
| Uduthorehalla | 2026-09-09 | 2026-10-04 | 39.59 | 24.09 | -15.50 | -39.15 | Eutrophic | VERIFIED |
| Jambhadhahalla | 2026-10-02 | 2026-10-12 | 21.34 | 24.97 | +3.63 | +17.00 | Eutrophic | VERIFIED |
| Tattihalla | 2026-10-12 | 2026-10-20 | 27.16 | 27.50 | +0.34 | +1.25 | Eutrophic | VERIFIED |
| Savehaklu | 2026-10-09 | 2026-10-12 | 25.24 | 23.28 | -1.96 | -7.76 | Eutrophic | VERIFIED |

Verified aggregates: **46** published reservoirs; **92** paired/history records; **42 E / 4 H**; **20 increasing / 26 decreasing**; latest range **16.18–67.65 µg/L**; pair acquisition extent **9 September–20 October 2026**; latest retained coverage **11.60–81.91%**. These are reservoir-date results; overlapping/shared satellite scenes make them unsuitable for describing 92 independent satellite acquisitions.

## Same-pass mosaic evidence

All four mosaics have persisted `_tile_index` ownership, no double-counting of polygon ownership, 100% data-footprint coverage, ≈100% geometry footprint and provider-confirmed matching date/platform/orbit/baseline. All listed constituent items returned HTTP 200 from the official catalog during this audit. Platform reported as Sentinel-2B for October 12/15 and Sentinel-2C for October 17/20; see exact source IDs below.

| Reservoir | Composite ID | Acquisition | µg/L | Valid pixels | Valid coverage % | Listed source tiles | Polygon ownership counts (source order) |
|---|---|---|---:|---:|---:|---:|---|
| basava-sagara | `MOSAIC_Sentinel2B_20261012T051739_62` | 2026-10-12T05:17:39.024000Z | 21.54588699 | 25197 | 73.7876 | 4 | {'0': 0, '1': 30488, '2': 3143, '3': 517} |
| basava-sagara | `MOSAIC_Sentinel2C_20261017T051821_62` | 2026-10-17T05:18:21.025000Z | 29.17161179 | 9586 | 28.0719 | 4 | {'0': 0, '1': 30488, '2': 3143, '3': 517} |
| malaprabha | `MOSAIC_Sentinel2B_20261015T052759_105` | 2026-10-15T05:27:59.024000Z | 23.27932739 | 16517 | 80.2108 | 2 | {'0': 17546, '1': 3046} |
| malaprabha | `MOSAIC_Sentinel2C_20261020T052841_105` | 2026-10-20T05:28:41.025000Z | 22.69149399 | 14213 | 69.0220 | 2 | {'0': 17546, '1': 3046} |

Constituent original source items (not synthetic mosaic IDs):

- **basava-sagara / 2026-10-12T05:17:39.024000Z**
  - `S2B_MSIL2A_20261012T051739_R062_T43PET_20261012T091927` — 2026-10-12T05:17:39.024000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PET_20261012T091927).
  - `S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927` — 2026-10-12T05:17:39.024000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927).
  - `S2B_MSIL2A_20261012T051739_R062_T43QEU_20261012T091927` — 2026-10-12T05:17:39.024000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QEU_20261012T091927).
  - `S2B_MSIL2A_20261012T051739_R062_T43QFU_20261012T091927` — 2026-10-12T05:17:39.024000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261012T051739_R062_T43QFU_20261012T091927).
- **basava-sagara / 2026-10-17T05:18:21.025000Z**
  - `S2C_MSIL2A_20261017T051821_R062_T43PET_20261017T102804` — 2026-10-17T05:18:21.025000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261017T051821_R062_T43PET_20261017T102804).
  - `S2C_MSIL2A_20261017T051821_R062_T43PFT_20261017T102804` — 2026-10-17T05:18:21.025000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261017T051821_R062_T43PFT_20261017T102804).
  - `S2C_MSIL2A_20261017T051821_R062_T43QEU_20261017T102804` — 2026-10-17T05:18:21.025000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261017T051821_R062_T43QEU_20261017T102804).
  - `S2C_MSIL2A_20261017T051821_R062_T43QFU_20261017T102804` — 2026-10-17T05:18:21.025000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261017T051821_R062_T43QFU_20261017T102804).
- **malaprabha / 2026-10-15T05:27:59.024000Z**
  - `S2B_MSIL2A_20261015T052759_R105_T43PDT_20261015T090952` — 2026-10-15T05:27:59.024000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261015T052759_R105_T43PDT_20261015T090952).
  - `S2B_MSIL2A_20261015T052759_R105_T43PET_20261015T090952` — 2026-10-15T05:27:59.024000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261015T052759_R105_T43PET_20261015T090952).
- **malaprabha / 2026-10-20T05:28:41.025000Z**
  - `S2C_MSIL2A_20261020T052841_R105_T43PDT_20261020T101804` — 2026-10-20T05:28:41.025000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261020T052841_R105_T43PDT_20261020T101804).
  - `S2C_MSIL2A_20261020T052841_R105_T43PET_20261020T101804` — 2026-10-20T05:28:41.025000Z — [provider item](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261020T052841_R105_T43PET_20261020T101804).

## All 92 numerical and persistence checks

For every row: six bands and masks load; TIFF full array equals saved NPZ chlorophyll (including NaNs); TIFF resolution is 60×60 m in EPSG:32643; independently rasterized polygon equals the saved polygon mask; RGB bytes reproduce from the saved bands; algorithm-valid pixel counts/coverage match the manifest; both pixel-count/coverage gates pass. The independent **float32 median error is zero for every record**. The column below reports the float64 median error for a more demanding precision comparison. “Mask unavailable” means SCL not retained, not that a numerical concentration is unavailable.

| Reservoir | Acquisition UTC | Scene/composite item ID | Valid pixels | Coverage % | Float64 median abs. error µg/L | SCL-mask reproduction |
|---|---|---|---:|---:|---:|---|
| krs | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFP_20261009T101803` | 7967 | 29.69548 | 4.82669528e-06 | VERIFIED |
| krs | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927` | 17505 | 65.24656 | 3.24279861e-06 | VERIFIED |
| bhadra | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PER_20261009T101803` | 22325 | 71.51552 | 1.71686288e-06 | VERIFIED |
| bhadra | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 25065 | 80.29279 | 1.46172868e-06 | VERIFIED |
| tungabhadra | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFS_20261012T091927` | 40407 | 89.81928 | 4.14688405e-07 | VERIFIED |
| tungabhadra | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFS_20261017T102804` | 31965 | 71.05386 | 5.09724463e-06 | VERIFIED |
| supa | 2026-10-10T05:27:31.025000Z | `S2C_MSIL2A_20261010T052731_R105_T43PDS_20261010T102100` | 18104 | 67.85607 | 1.18021978e-06 | VERIFIED |
| supa | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 18533 | 69.46402 | 4.80393761e-06 | VERIFIED |
| varahi | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PER_20261009T101803` | 1605 | 12.87399 | 9.15132485e-07 | UNVERIFIED — SCL absent |
| varahi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 6269 | 50.28475 | 2.36865165e-06 | UNVERIFIED — SCL absent |
| vani-vilasa | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFR_20261009T101803` | 7914 | 63.53565 | 1.37787984e-06 | VERIFIED |
| vani-vilasa | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFR_20261012T091927` | 7950 | 63.82466 | 6.61550615e-07 | VERIFIED |
| kabini | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFP_20261009T101803` | 3509 | 21.75989 | 2.73072086e-06 | VERIFIED |
| kabini | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927` | 10417 | 64.59754 | 3.20118816e-06 | VERIFIED |
| harangi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927` | 2357 | 52.55295 | 4.75932594e-06 | VERIFIED |
| harangi | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PEP_20261017T102804` | 585 | 13.04348 | 9.51124861e-07 | VERIFIED |
| hemavathi | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFQ_20261009T101803` | 2581 | 18.48060 | 4.0846433e-06 | VERIFIED |
| hemavathi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFQ_20261012T091927` | 9897 | 70.86496 | 1.83190312e-06 | VERIFIED |
| almatti | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QEU_20261009T101803` | 36206 | 61.23326 | 3.19298255e-06 | VERIFIED |
| almatti | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QEU_20261012T091927` | 43831 | 74.12901 | 7.54171037e-07 | VERIFIED |
| linganamakki | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PDR_20261009T101803` | 29646 | 38.92135 | 2.13123462e-06 | VERIFIED |
| linganamakki | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927` | 35089 | 46.06730 | 2.29374069e-06 | VERIFIED |
| markonahalli | 2026-10-14T05:07:51.025000Z | `S2C_MSIL2A_20261014T050751_R019_T43PFQ_20261014T100514` | 594 | 19.29825 | 5.21866625e-06 | VERIFIED |
| markonahalli | 2026-10-19T05:08:19.024000Z | `S2B_MSIL2A_20261019T050819_R019_T43PFQ_20261019T085221` | 427 | 13.87264 | 4.60492625e-07 | VERIFIED |
| yagachi | 2026-09-27T05:16:51.025000Z | `S2C_MSIL2A_20260927T051651_R062_T43PEQ_20260927T101415` | 1561 | 50.55052 | 1.42895979e-06 | VERIFIED |
| yagachi | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEQ_20261012T091927` | 506 | 16.38601 | 5.78398811e-06 | VERIFIED |
| hidkal | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDT_20261015T090952` | 6594 | 37.65848 | 1.91843888e-06 | VERIFIED |
| hidkal | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDT_20261020T101804` | 14343 | 81.91319 | 1.74037273e-06 | VERIFIED |
| nugu | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFP_20261009T101803` | 854 | 31.14515 | 4.00734883e-06 | VERIFIED |
| nugu | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFP_20261017T102804` | 1336 | 48.72356 | 1.60697317e-06 | VERIFIED |
| kadra | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDS_20261015T090952` | 3736 | 51.71650 | 4.48067642e-06 | VERIFIED |
| kadra | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 5347 | 74.01717 | 8.04519534e-07 | VERIFIED |
| basava-sagara | 2026-10-12T05:17:39.024000Z | `MOSAIC_Sentinel2B_20261012T051739_62` | 25197 | 73.78763 | 1.10754544e-06 | VERIFIED |
| basava-sagara | 2026-10-17T05:18:21.025000Z | `MOSAIC_Sentinel2C_20261017T051821_62` | 9586 | 28.07192 | 1.07048294e-06 | VERIFIED |
| malaprabha | 2026-10-15T05:27:59.024000Z | `MOSAIC_Sentinel2B_20261015T052759_105` | 16517 | 80.21076 | 2.46786783e-06 | VERIFIED |
| malaprabha | 2026-10-20T05:28:41.025000Z | `MOSAIC_Sentinel2C_20261020T052841_105` | 14213 | 69.02195 | 2.71199203e-06 | VERIFIED |
| gerusoppa | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDR_20261015T090952` | 752 | 44.47073 | 1.03397474e-06 | VERIFIED |
| gerusoppa | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDR_20261020T101804` | 739 | 43.70195 | 4.32899117e-07 | VERIFIED |
| kodasalli | 2026-10-02T05:32:41.024000Z | `S2A_MSIL2A_20261002T053241_R105_T43PDS_20261002T101803` | 2171 | 52.63030 | 1.28345829e-06 | VERIFIED |
| kodasalli | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 2008 | 48.67879 | 3.34693959e-06 | VERIFIED |
| karanja | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 9119 | 89.47214 | 3.23978899e-06 | VERIFIED |
| karanja | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 7741 | 75.95173 | 2.51781503e-06 | VERIFIED |
| kanva | 2026-10-04T05:06:51.025000Z | `S2C_MSIL2A_20261004T050651_R019_T43PGQ_20261004T102617` | 374 | 37.89260 | 2.99848661e-06 | VERIFIED |
| kanva | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGQ_20261009T090953` | 154 | 15.60284 | 4.03036022e-06 | VERIFIED |
| manchanabele | 2026-10-14T05:07:51.025000Z | `S2C_MSIL2A_20261014T050751_R019_T43PGQ_20261014T100514` | 387 | 53.15934 | 4.98624443e-06 | VERIFIED |
| manchanabele | 2026-10-19T05:08:19.024000Z | `S2B_MSIL2A_20261019T050819_R019_T43PGQ_20261019T085221` | 292 | 40.10989 | 1.77927166e-05 | VERIFIED |
| suvarnavathy | 2026-09-29T05:06:49.024000Z | `S2B_MSIL2A_20260929T050649_R019_T43PGP_20260929T091314` | 171 | 15.70248 | 2.55542042e-06 | VERIFIED |
| suvarnavathy | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGP_20261009T090953` | 271 | 24.88522 | 5.17568916e-06 | VERIFIED |
| taraka | 2026-10-07T05:17:11.025000Z | `S2C_MSIL2A_20261007T051711_R062_T43PFP_20261007T100505` | 546 | 44.86442 | 2.76914891e-06 | VERIFIED |
| taraka | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFP_20261012T091927` | 753 | 61.87346 | 2.5347649e-06 | VERIFIED |
| votehole | 2026-09-27T05:16:51.025000Z | `S2C_MSIL2A_20260927T051651_R062_T43PEQ_20260927T101415` | 614 | 46.09610 | 2.56857697e-06 | VERIFIED |
| votehole | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEQ_20261012T091927` | 579 | 43.46847 | 1.56591031e-06 | VERIFIED |
| bennethora | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 2497 | 53.04865 | 4.42585501e-07 | VERIFIED |
| bennethora | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 1777 | 37.75228 | 1.02070809e-06 | VERIFIED |
| chandrampalli | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGV_20261009T101803` | 554 | 60.81229 | 4.36141079e-07 | VERIFIED |
| chandrampalli | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 557 | 61.14160 | 7.79941857e-07 | VERIFIED |
| dharma | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PDS_20261009T101803` | 756 | 61.86579 | 9.61063499e-07 | VERIFIED |
| dharma | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDS_20261012T091927` | 465 | 38.05237 | 4.00876531e-06 | VERIFIED |
| upper-tunga | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PER_20261009T101803` | 835 | 26.39064 | 2.60003256e-06 | VERIFIED |
| upper-tunga | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 1635 | 51.67509 | 5.03294608e-07 | VERIFIED |
| chikkahole | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGP_20261009T090953` | 79 | 24.08537 | 8.71452063e-07 | VERIFIED |
| chikkahole | 2026-10-14T05:07:51.025000Z | `S2C_MSIL2A_20261014T050751_R019_T43PGP_20261014T100514` | 62 | 18.90244 | 1.97583958e-06 | VERIFIED |
| chiklihole | 2026-10-07T05:17:11.025000Z | `S2C_MSIL2A_20261007T051711_R062_T43PEP_20261007T100505` | 27 | 15.60694 | 1.05152426e-06 | VERIFIED |
| chiklihole | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PEP_20261012T091927` | 45 | 26.01156 | 3.15866168e-06 | VERIFIED |
| hattikuni | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGU_20261009T101803` | 120 | 36.03604 | 9.83953463e-07 | VERIFIED |
| hattikuni | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGU_20261012T091927` | 113 | 33.93393 | 1.53743269e-06 | VERIFIED |
| narihalla | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PFS_20261009T101803` | 334 | 54.39739 | 3.38974147e-06 | VERIFIED |
| narihalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFS_20261012T091927` | 326 | 53.09446 | 3.0348599e-07 | VERIFIED |
| upper-mullamari | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 361 | 48.71795 | 1.97955882e-06 | VERIFIED |
| upper-mullamari | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 351 | 47.36842 | 2.46786783e-06 | VERIFIED |
| lower-mullamari | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGV_20261009T101803` | 517 | 21.44338 | 9.96880775e-07 | VERIFIED |
| lower-mullamari | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 1011 | 41.93281 | 2.08325027e-06 | VERIFIED |
| gundal | 2026-10-04T05:06:51.025000Z | `S2C_MSIL2A_20261004T050651_R019_T43PGP_20261004T102617` | 87 | 15.28998 | 3.28195402e-07 | VERIFIED |
| gundal | 2026-10-09T05:07:19.024000Z | `S2B_MSIL2A_20261009T050719_R019_T43PGP_20261009T090953` | 66 | 11.59930 | 1.39923639e-06 | VERIFIED |
| gandorinala | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43QGV_20261009T101803` | 641 | 34.95093 | 3.02586738e-07 | VERIFIED |
| gandorinala | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 698 | 38.05889 | 2.98900167e-06 | VERIFIED |
| maskinala | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927` | 102 | 19.61538 | 5.21121109e-07 | VERIFIED |
| maskinala | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFT_20261017T102804` | 106 | 20.38462 | 2.32786712e-06 | VERIFIED |
| chulkinala | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43QGV_20261012T091927` | 880 | 73.76362 | 1.10674584e-07 | VERIFIED |
| chulkinala | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43QGV_20261017T102804` | 656 | 54.98743 | 2.15546268e-06 | VERIFIED |
| harinala | 2026-10-10T05:27:31.025000Z | `S2C_MSIL2A_20261010T052731_R105_T43PDT_20261010T102100` | 149 | 25.73402 | 4.40488195e-06 | VERIFIED |
| harinala | 2026-10-15T05:27:59.024000Z | `S2B_MSIL2A_20261015T052759_R105_T43PDT_20261015T090952` | 149 | 25.73402 | 1.73766071e-06 | VERIFIED |
| hirehalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PFT_20261012T091927` | 1431 | 72.16339 | 3.77286279e-06 | VERIFIED |
| hirehalla | 2026-10-17T05:18:21.025000Z | `S2C_MSIL2A_20261017T051821_R062_T43PFT_20261017T102804` | 1142 | 57.58951 | 3.76243559e-06 | VERIFIED |
| uduthorehalla | 2026-09-09T05:06:49.024000Z | `S2B_MSIL2A_20260909T050649_R019_T43PGP_20260909T085145` | 76 | 30.03953 | 4.10986839e-06 | VERIFIED |
| uduthorehalla | 2026-10-04T05:06:51.025000Z | `S2C_MSIL2A_20261004T050651_R019_T43PGP_20261004T102617` | 82 | 32.41107 | 2.84572654e-06 | VERIFIED |
| jambhadhahalla | 2026-10-02T05:16:49.024000Z | `S2B_MSIL2A_20261002T051649_R062_T43PER_20261002T091946` | 140 | 36.45833 | 3.85917046e-06 | VERIFIED |
| jambhadhahalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PER_20261012T091927` | 236 | 61.45833 | 4.74798221e-06 | VERIFIED |
| tattihalla | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDS_20261012T091927` | 1503 | 38.90758 | 3.38223559e-06 | VERIFIED |
| tattihalla | 2026-10-20T05:28:41.025000Z | `S2C_MSIL2A_20261020T052841_R105_T43PDS_20261020T101804` | 1503 | 38.90758 | 2.69627691e-07 | VERIFIED |
| savehaklu | 2026-10-09T05:22:41.024000Z | `S2A_MSIL2A_20261009T052241_R062_T43PDR_20261009T101803` | 286 | 14.25012 | 3.19311325e-06 | VERIFIED |
| savehaklu | 2026-10-12T05:17:39.024000Z | `S2B_MSIL2A_20261012T051739_R062_T43PDR_20261012T091927` | 719 | 35.82461 | 2.46786783e-06 | VERIFIED |

## Scientific references: exact external evidence

- **Gilerson et al. (2010)** — [author institution publication/abstract](https://digitalcommons.unl.edu/calmitpapers/3/), [PubMed bibliographic record](https://pubmed.ncbi.nlm.nih.gov/21164758/), [DOI](https://doi.org/10.1364/OE.18.024109). Authorship, venue, date and aquatic red/NIR basis match. Original full-text download returned 403; not represented as read.
- **Exact coefficient corroboration:** De Keukelaere et al., “Airborne Drones for Water Quality Mapping in Inland, Transitional and Coastal Waters—MapEO Water Data Processing and Validation,” *Remote Sensing* 15, 1345 (2023), p. 5, Eq. (9), [institutional full text](https://dspace.stir.ac.uk/retrieve/87946103-2630-4dc6-8e3c-8f1e5b3dd6ed/remotesensing-15-01345.pdf), DOI 10.3390/rs15051345. This is primary research supporting the expression, not an addition already present in the unchanged NEERWATCH paper bibliography. Its water-leaving reflectance context reinforces the BOA-transfer caveat.
- **Assaf et al. (2025)** — [institutional full text](https://services.uop.edu.jo/InstructorProfile/files/Publication202571915713.pdf), [DOI](https://doi.org/10.1007/s40808-025-02543-4). Read 26-page PDF; p.1 supports six-regressor and feature-importance related-work claims. This supports no NEERWATCH accuracy claim.
- **ESA:** [S2 Products](https://sentiwiki.copernicus.eu/web/s2-products), Level-2A product radiometry, supports metadata-dependent additive offsets and zero-DN no-data handling.
- **EPA:** [National Lakes Assessment trophic state](https://nationallakesassessment.epa.gov/webreport/#trophic-state) directly supports the four threshold intervals. It does not establish local Karnataka regulatory thresholds.
- **Planetary Computer:** individual original source-item links above were fetched successfully. [Collection](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a) identifies catalog provenance; successful catalog access is not raw-DN validation for every cached product.
- **CWC:** [National Register of Large Dams 2019](https://www.cwc.gov.in/sites/default/files/nrld-2019.pdf); actual downloaded register and stored per-reservoir identity records inspected. Dam register is not the source of the OSM water polygons.
- **OSM:** [copyright/license](https://www.openstreetmap.org/copyright); ODbL attribution in paper/map context is appropriate.
- **WaterQual:** [upstream repository](https://github.com/iliasmachairas/WaterQual); executing vendored NDCI code/import is the implementation proof, not a claim of scientific concentration validation.

## Reproducible safe checks and audit artifacts

Backend command actually executed from the repository, with no project caches created:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider --basetemp=/tmp/neerwatch-audit-pytest -q
```

Result: **60 passed, 1 warning in 27.28 s**. Warning: deprecated Starlette/httpx TestClient integration. This suite includes synthetic *test fixtures* to exercise control flow; those fixtures were not used as dashboard measurements or paper results.

Temporary audit evidence (not committed or substituted for project source):

- `/tmp/neerwatch-audit.py` — independent numeric/mask/grid/persistence/table/API audit.
- `/tmp/neerwatch-audit-results.json` and `.log` — per-observation values and API results.
- `/tmp/neerwatch-audit-stac.json` — 12 fetched official constituent item metadata records.
- `/tmp/neerwatch-audit-tests.log` — complete fresh pytest output.
- `/tmp/neerwatch-audit-build.log` — successful fresh Vite production build, with output outside the project.
- `/tmp/neerwatch-audit-ui.mjs`, `/tmp/neerwatch-audit-ui-results.json`, `/tmp/neerwatch-audit-ui.log` — fresh current-JSX DOM checks (output redirected away from the existing project report).
- `/tmp/neerwatch_audit_server.py` — temporary read-only middleware wrapper around current backend; no repository code changes.
- `/tmp/neerwatch-audit-before.json` — protected-file hash baseline.

Temporary files may be cleared by the operating system. The substantive outcomes and complete result ledger are embedded above so this audit is self-contained.

## Final integrity and submission decision

Protected-file SHA-256 recheck: **1487 existing files checked; 0 changed** before writing this new audit. Both PDFs, their sources, all project code/model/data files in the baseline, and the prior implementation evidence remain unchanged.

**Architecture:** accurate for the primary empirical pipeline, with partial historical provenance for two records and no all-backend/exhaustive interpretation. **Paper:** core equation, thresholds, software components and all published numerical results are supported; blanket legacy-ML and per-manifest-completeness wording is not. Numerical precision and source-access qualifications should be tightened. Therefore **both documents should not receive an unconditional “safe to submit unchanged” sign-off**. Targeted document corrections and completed author details are needed; no code/data/document corrections were performed as part of this audit.

Audit cleanup: the temporary 8011 server was stopped and its browser tab closed. Fresh Vite build files are byte-for-byte identical to existing frontend/dist. Final protected-file recheck still shows zero content changes.
