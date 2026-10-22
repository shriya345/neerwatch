# NEERWATCH public inventory repair — 22 October 2026

## Counts

- Public reservoirs: 8
- Removed unwanted tank names: 20.
- Excluded coordinate-only CWC inventory entries: 23 (20 tanks and 3 other entries).
- Total internal pending records: 32; no public detail, image, report, boundary, processing or export access.
- Public verified water polygons: 8.
- Public reservoirs with valid Sentinel-2 concentration/category: 8.
- Public reservoirs with two compatible acquisition dates and valid percentage change: 8.
- Public reservoirs with matching true-colour image, chlorophyll map and GeoTIFF: 8.
- Public Sentinel-2 observation records: 16.

## Per-reservoir verification

PASS here refers to actual geometry, saved spectral data, live API and executed React/Leaflet state checks. Visual layout/geographic overlay inspection remains incomplete because browser control is disabled. No row is claimed visually verified in this repair.

| Reservoir | Identity / polygon provenance | Location / CRS | Boundary rendered / popup / polygon click | Valid S2 / EPA | Two dates / change | RGB / map / scene match | React auto-load / navigation | Restart / fresh DOM | Visual browser |
|---|---|---|---|---|---|---|---|---|
| KRS | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |
| Bhadra | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |
| Tungabhadra | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |
| Supa | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |
| Varahi | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |
| Vani Vilasa Sagara | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |
| Kabini | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |
| Harangi | PASS | PASS | PASS (DOM) | PASS | PASS | PASS | PASS | PASS | INCOMPLETE |

## Real observation values

All values are experimental Gilerson 2010 two-band Sentinel-2 L2A BOA screening estimates, not laboratory measurements. No concentration was hardcoded, copied from KRS or substituted from Sentinel-3.

| Reservoir | Earlier UTC date | Earlier µg/L | Latest UTC date | Latest µg/L | Change | EPA category |
|---|---|---:|---|---:|---:|---|
| KRS | 2026-10-09T05:22:41.024000Z | 25.15318 | 2026-10-12T05:17:39.024000Z | 24.72256 | -1.712% | Eutrophic |
| Bhadra | 2026-10-09T05:22:41.024000Z | 25.35455 | 2026-10-12T05:17:39.024000Z | 23.97058 | -5.458% | Eutrophic |
| Tungabhadra | 2026-10-12T05:17:39.024000Z | 27.33957 | 2026-10-17T05:18:21.025000Z | 42.19335 | +54.331% | Hypereutrophic |
| Supa | 2026-10-10T05:27:31.025000Z | 22.68390 | 2026-10-20T05:28:41.025000Z | 25.31980 | +11.620% | Eutrophic |
| Varahi | 2026-10-09T05:22:41.024000Z | 24.79434 | 2026-10-12T05:17:39.024000Z | 22.86766 | -7.771% | Eutrophic |
| Vani Vilasa Sagara | 2026-10-09T05:22:41.024000Z | 22.31195 | 2026-10-12T05:17:39.024000Z | 21.65385 | -2.950% | Eutrophic |
| Kabini | 2026-10-09T05:22:41.024000Z | 24.84025 | 2026-10-12T05:17:39.024000Z | 23.84874 | -3.992% | Eutrophic |
| Harangi | 2026-10-12T05:17:39.024000Z | 24.56827 | 2026-10-17T05:18:21.025000Z | 32.37011 | +31.756% | Hypereutrophic |

## Boundary evidence

All public boundaries are existing OpenStreetMap water polygons (ODbL), an established geospatial source, not circles or dam coordinates. The polygons were checked for topology, geographic location against registered reservoir coordinates, Karnataka-region bounds, Sentinel-2 overlap, water-mask pixels and EPSG:32643 raster consistency. Saved record source URLs and original boundary source metadata are retained. These are not represented as surveyed government cadastral boundaries.

| Reservoir | Water polygon source |
|---|---|
| KRS | https://www.openstreetmap.org/relation/9050201 |
| Bhadra | https://www.openstreetmap.org/relation/371833 |
| Tungabhadra | https://www.openstreetmap.org/relation/1593736 |
| Supa | https://www.openstreetmap.org/relation/5998514 |
| Varahi | https://www.openstreetmap.org/relation/11527523 |
| Vani Vilasa Sagara | https://www.openstreetmap.org/relation/371829 |
| Kabini | https://www.openstreetmap.org/relation/5867868 |
| Harangi | https://www.openstreetmap.org/relation/5838873 |

## What changed

The public source data/reservoirs.json now contains only operational records. Excluded records and reasons are retained under data/internal/pending-reservoirs.json, which is not mounted as a static directory or exposed through the API. Public inventory is additionally gated on evidence at request time. All public reservoir routes, exports and reports derive from that filtered registry; direct access to pending IDs is rejected with HTTP 404.

Same-method pairing now also checks atmospheric correction, analysis resolution, shoreline/cloud buffers, minimum pixel/coverage settings, algorithm range and aggregation, and requires different acquisition dates. A positive earlier value is required for percentage change.

Map selection draws the selected real polygon, fits its bounds, highlights it, names it in a popup and handles polygon clicks using the same workspace selection callback as the list. Existing colors/layout were retained.

Vani Vilasa uses the existing consistent ID vani-vilasa in selector, detail API and cache directory. Its persisted concentration, dates and percentage load on selection and in fresh React sessions. No new processing click is needed.

Kabini and Harangi were processed sequentially in small batches (two observations each), verified and admitted. Hemavathi, Almatti, Linganamakki and other incomplete entries remain pending; expanding them was not allowed to keep them on the public site before readiness.

## Exact changed/added implementation and test files

- data/reservoirs.json
- data/internal/pending-reservoirs.json
- backend/readiness.py
- backend/active.py
- backend/monitoring.py
- backend/main.py
- frontend/src/main.jsx
- pipeline/sentinel2_chlorophyll.py (internal-only pending lookup for batch preprocessing)
- scripts/verify_live_processing.py
- scripts/report_public_readiness.py
- scripts/frontend-check/check.mjs
- scripts/frontend-check/package.json
- tests/test_public_readiness.py
- tests/test_system.py (replace obsolete minimum-count expectation with operational registry checks)
- tests/test_sentinel2.py (replace obsolete 40-entry expectation with strict public inventory checks)
- IMPLEMENTATION.md
- data/sentinel2/kabini/* and data/sentinel2/harangi/* (genuine new scenes, arrays, manifests, images and rasters)

## Tests and reproducible evidence

- Backend suite: 51 passed; one pre-existing Starlette/httpx deprecation warning.
- Frontend production build: passed.
- Backend restarted; all public inventory/results loaded from persisted data afterward.
- Real React bundle and real Leaflet executed against the running API in jsdom: 16 successful workspace loads across two fresh DOM sessions. Each loaded nonempty concentration/date/category/change and a real image URL. Polygon SVG, popup name and click callback passed for every reservoir. This is frontend state/integration evidence, not a visual browser screenshot or layout test.
- All pending IDs checked for HTTP 404 on detail, boundary, processing status, processing POST, images and reports; pending names absent from CSV export.
- Live spectral audit checked each public reservoir concentration against saved band arrays and GeoTIFF pixels, metadata CRS, source scene IDs, images and EPA category.
- Evidence: output/processing-verification.json and output/public-frontend-state-verification.json.
- Frontend test dependencies: install in scripts/frontend-check with npm install, then npm test. The test expects the backend at http://127.0.0.1:8010.

## Remaining limitations

Browser control is disabled in Work settings. Final visual layout/overlay inspection is incomplete; the site is not claimed fully visually verified. The application remains running locally at http://127.0.0.1:8010; no external production deployment was supplied or changed.

Full ACOLITE water-specific correction and local field calibration are still absent. Satellite-derived chlorophyll-a estimates have not yet been validated against Karnataka field measurements. EPA categories describe trophic screening, not toxicity or water safety. No synthetic data were added.

## Pending inventory

| Record | Pending reason |
|---|---|
| Hemavathi | Two valid comparable acquisitions required |
| Almatti | Two valid comparable acquisitions required |
| Basava Sagara | Two valid comparable acquisitions required |
| Linganamakki | Two valid comparable acquisitions required |
| Shanti Sagara | Two valid comparable acquisitions required |
| Markonahalli | Two valid comparable acquisitions required |
| Yagachi | Two valid comparable acquisitions required |
| Malaprabha (Renuka Sagara) | Two valid comparable acquisitions required |
| Hidkal | Two valid comparable acquisitions required |
| Thonnur Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Madaga Tank (old) | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Kottur Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Boranakanive Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Maidal Amanikere Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Hesaraghatta Reservoir | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Deepambudikere Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Kadaba Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Kunigal Do dakere Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Nidasale Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Nittur Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Ranikere Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Madagamasur Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Mavathur Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Mavinahole Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Sowlanga Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Doddaladahalli Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Tippagondana Hally | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Anjanapura Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Maralvadi Dam | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Tumbodi Amanikere Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Ballasamudra Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
| Markandeya Tank | Verified water boundary provenance required; Two valid comparable acquisitions required |
