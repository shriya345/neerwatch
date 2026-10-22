# Functional Karnataka reservoir coverage expansion

## Outcome
Public operational reservoirs: 16 (original eight preserved; 8 admitted after preprocessing).
Internal pending records: 26.
No ordinary tanks, forecasting, redesign, concentration substitution or relaxed quality masks were added.

## Actual results

| Reservoir | Boundary | Earlier acquisition | Latest acquisition | Latest chlorophyll-a µg/L | Change % | EPA category | RGB | Chlorophyll map |
|---|---|---|---|---:|---:|---|---|---|
| KRS | [Verified polygon](https://www.openstreetmap.org/relation/9050201) | 2026-10-09 | 2026-10-12 | 24.72 | -1.71 | Eutrophic | PASS | PASS |
| Bhadra | [Verified polygon](https://www.openstreetmap.org/relation/371833) | 2026-10-09 | 2026-10-12 | 23.97 | -5.46 | Eutrophic | PASS | PASS |
| Tungabhadra | [Verified polygon](https://www.openstreetmap.org/relation/1593736) | 2026-10-12 | 2026-10-17 | 42.19 | +54.33 | Hypereutrophic | PASS | PASS |
| Supa | [Verified polygon](https://www.openstreetmap.org/relation/5998514) | 2026-10-10 | 2026-10-20 | 25.32 | +11.62 | Eutrophic | PASS | PASS |
| Varahi | [Verified polygon](https://www.openstreetmap.org/relation/11527523) | 2026-10-09 | 2026-10-12 | 22.87 | -7.77 | Eutrophic | PASS | PASS |
| Vani Vilasa Sagara | [Verified polygon](https://www.openstreetmap.org/relation/371829) | 2026-10-09 | 2026-10-12 | 21.65 | -2.95 | Eutrophic | PASS | PASS |
| Kabini | [Verified polygon](https://www.openstreetmap.org/relation/5867868) | 2026-10-09 | 2026-10-12 | 23.85 | -3.99 | Eutrophic | PASS | PASS |
| Harangi | [Verified polygon](https://www.openstreetmap.org/relation/5838873) | 2026-10-12 | 2026-10-17 | 32.37 | +31.76 | Hypereutrophic | PASS | PASS |
| Hemavathi | [Verified polygon](https://www.openstreetmap.org/relation/6323615) | 2026-10-09 | 2026-10-12 | 24.26 | -0.45 | Eutrophic | PASS | PASS |
| Almatti | [Verified polygon](https://www.openstreetmap.org/relation/1585775) | 2026-10-09 | 2026-10-12 | 20.98 | -14.32 | Eutrophic | PASS | PASS |
| Linganamakki | [Verified polygon](https://www.openstreetmap.org/relation/371834) | 2026-10-09 | 2026-10-12 | 23.78 | -2.42 | Eutrophic | PASS | PASS |
| Markonahalli | [Verified polygon](https://www.openstreetmap.org/way/374160092) | 2026-10-14 | 2026-10-19 | 21.81 | -20.23 | Eutrophic | PASS | PASS |
| Yagachi | [Verified polygon](https://www.openstreetmap.org/way/202809162) | 2026-09-27 | 2026-10-12 | 25.22 | -1.21 | Eutrophic | PASS | PASS |
| Hidkal | [Verified polygon](https://www.openstreetmap.org/relation/1611534) | 2026-10-15 | 2026-10-20 | 20.39 | -6.16 | Eutrophic | PASS | PASS |
| Nugu | [Verified polygon](https://www.openstreetmap.org/way/33840471) | 2026-10-09 | 2026-10-17 | 23.54 | -8.27 | Eutrophic | PASS | PASS |
| Kadra | [Verified polygon](https://www.openstreetmap.org/relation/383565) | 2026-10-15 | 2026-10-20 | 24.67 | -10.38 | Eutrophic | PASS | PASS |

Both dates use the existing Gilerson 2010 two-band Sentinel-2 L2A BOA screening method, matching atmospheric correction and 60 m grid, shoreline/cloud exclusions, positive-reflectance checks, minimum 25 pixels/10% coverage and 1–100 µg/L project algorithm screening range. Concentrations are medians of valid pixels. The concentration, RGB and chlorophyll map use the same acquisition.

## Government identity verification

Government records used: [Central Water Commission NRLD 2019](https://www.cwc.gov.in/sites/default/files/nrld-2019.pdf) and [Karnataka Legislative Assembly questions, 18 July 2016](https://kla.kar.nic.in/assembly/questions/lasq18072016.pdf) for Markonahalli. Government inventory dam locations were independently compared to the original OpenStreetMap reservoir water polygons. Names, PICs, physical PDF pages and distances are saved in data/internal/coverage-identity-audit.json. These government dam points were not used as fabricated water boundaries.

## New-reservoir validation

| New reservoir | Identity / polygon | Two spectral calculations / rasters | Comparable pair / EPA | Live API | React / Leaflet sessions | Visual inspection |
|---|---|---|---|---|---|
| Hemavathi | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |
| Almatti | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |
| Linganamakki | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |
| Markonahalli | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |
| Yagachi | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |
| Hidkal | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |
| Nugu | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |
| Kadra | PASS | PASS | PASS | PASS | PASS | INCOMPLETE: browser disabled |

## Candidate failures and exclusions

- basava-sagara: No valid Sentinel-2 concentration in the 60-day search window (59 scenes). No scene covers at least 95% of the reservoir.
- malaprabha: No valid Sentinel-2 concentration in the 60-day search window (59 scenes). No scene covers at least 95% of the reservoir.

Basava Sagara spans multiple Sentinel-2 tiles; its best single-tile footprint is about 89.2%, below the unchanged 95% required footprint. It remains pending. No partial-reservoir estimate was published as a whole-reservoir value.
Kodasalli and Karanja remain unadmitted: project water polygons and processed pairs have not been verified. Nugu and Kadra were attempted after the first eight candidates to compensate for footprint failures. Admission stopped within the requested 15–20 operational range.

## Real verification

- Original eight latest/history/boundary file hashes preserved byte-for-byte (tests/test_coverage_integrity.py).
- Each newly admitted pair was independently recomputed from its saved B04/B05 arrays; median, valid pixel count, raster pixels, scene ID and CRS matched. Both source arrays contain real SCL water pixels overlapping the polygon.
- All public API details, true-colour images, chlorophyll maps, boundaries and PDF downloads checked. Pending IDs remain HTTP 404.
- The actual React bundle and Leaflet run against the real localhost API in two fresh jsdom sessions, loading every public workspace, matching concentrations and verifying polygon SVGs, named popups and click callbacks. These are frontend state tests, not visual browser tests.
- Backend restarted and the checks repeated against persisted data.
- Backend suite: 53 passed, with one existing Starlette/httpx deprecation warning. Frontend production build passed.

## Evidence and changed files

- data/reservoirs.json — only audited public additions.
- data/internal/pending-reservoirs.json — excluded candidates retained with reasons.
- data/internal/coverage-identity-audit.json — official identity/location audit.
- data/internal/original-eight-coverage-snapshot.json — original output preservation hashes.
- data/sentinel2/{new reservoir}/* — genuine two-date bands, masks, manifests, PNGs and GeoTIFFs.
- scripts/expand_verified_coverage.py — sequential small-batch preprocessing.
- scripts/expand_additional_candidates.py — Nugu/Kadra sequential follow-up batch.
- data/boundaries/nugu.geojson and data/boundaries/kadra.geojson — real sourced OpenStreetMap polygons.
- scripts/audit_candidate_identities.py — government record/polygon matching.
- scripts/admit_coverage_candidates.py — independent spectral-pair checks before admission.
- scripts/report_coverage_expansion.py — this generated report.
- tests/test_coverage_integrity.py — original-eight preservation and new identity/readiness checks.
- tests/test_sentinel2.py — operational count now permits the requested 15–20 range.
- output/coverage-batch-results.json and output/coverage-admission-audit.json — candidate outcomes.
- output/processing-verification.json and output/public-frontend-state-verification.json — live API/spectral and React/Leaflet evidence.

## Limitations

Browser control remains disabled in Work settings, so final visual layout and geographic-overlay inspection are incomplete. No claim of full visual validation is made. The served application is local at http://127.0.0.1:8010; no remote production deployment was changed.

Satellite-derived chlorophyll-a estimates have not yet been validated against Karnataka field measurements. Full aquatic atmospheric correction/local calibration remain absent; these experimental surface-reflectance estimates and EPA trophic categories are not confirmed harmful-bloom or toxicity alerts.
