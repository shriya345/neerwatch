# Current phase: 46 operational reservoirs

NEERWATCH now publishes 46 complete reservoirs: the original 16 plus 30 independently audited additions. All public entries have verified polygons, two compatible Sentinel-2 observations, experimental chlorophyll estimates, EPA category, absolute/percentage change, matching RGB and heatmap, source arrays and GeoTIFF. Basava Sagara and Malaprabha now use same-date/orbit/baseline mosaics with >=95% coverage. The original 16 cache/history/boundary hashes are unchanged.

See [full 46-reservoir report](output/scale-to-46-report.md) and [verification CSV](output/scale-reservoir-verification.csv). There are 13 investigated candidates not published in this phase and 34 total internal inventory records including historical exclusions. No 140-reservoir publication was attempted.

Run from this project directory:

```sh
npm --prefix frontend run build
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

The comparison table supports name, concentration, increase, decrease and category sorting; previews and downloads use actual source scenes. All polygon boundaries are rendered and selectable. Media can be pinned to a saved acquisition with scene_id, avoiding an image/concentration mismatch during refresh. Visual browser inspection remains incomplete because browser control is disabled; actual React/Leaflet state and live API/spectral tests were run. Estimates remain unvalidated against Karnataka field measurements.

Previous phase counts below are historical and superseded.

---

# Functional coverage expansion — latest state

The public dashboard now contains 16 operational reservoirs, including eight verified additions. Original eight cache/history/boundary hashes are unchanged. All public entries have two compatible Sentinel-2 acquisitions, concentration, EPA category, percentage change, RGB and chlorophyll map. See [coverage expansion report](output/coverage-expansion-report.md). Basava Sagara and Malaprabha remain pending due to single-tile footprint coverage. There are 26 internal pending records in total.

Validation: 53 tests passed; frontend build passed; all 16 real React/Leaflet workspaces loaded across two fresh DOM sessions against the restarted live API. Visual browser verification remains incomplete because browser control is disabled.

Previous counts below are historical and superseded by this section.

---

# Public inventory repair

Current public inventory: 8 operational reservoirs; 32 records retained internally. All public entries require a verified water polygon, two compatible processed Sentinel-2 acquisitions, concentration/category/change and matching images/raster. See [public inventory repair report](output/public-inventory-repair-report.md) for per-reservoir evidence and limitations. Backend: 51 tests pass; frontend builds. React/Leaflet state verified against live API across two fresh DOM sessions. Visual browser verification remains incomplete because browser control is disabled.

The historical implementation notes below are retained for provenance and their earlier counts are superseded by this section.

---

# Local operation and verification

From `/Users/shriyahr/Documents/ChatGPT/Major/NEERWATCH`:

```sh
npm --prefix frontend run build
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

Open http://127.0.0.1:8010/. Current local environment symlinks the existing verified Python environment, frontend dependencies and original satellite cache. For a standalone copy, create a Python 3.12 virtual environment, install requirements-lock.txt, run npm ci in frontend, and copy required cache files rather than preserving machine-specific symlinks.

Tests: `.venv/bin/python -m pytest -q` (49 passed). Frontend production build passed. Actual KRS band tests check WaterQual NDCI, published Gilerson equation, valid-pixel counts, spatial metadata, raster pixel values and reservoir median. These demonstrate implementation agreement, not field accuracy. No Karnataka laboratory chlorophyll matches are available: no MAE/RMSE/bias is invented.

40 sites registered: original 17 water boundaries retained, 23 CWC inventory additions. Added sites have inventory points but require independently verified water polygons before satellite processing. Names retain official inventory spellings; unknown districts are null. Search handles names, known aliases and districts where supplied.

Six reservoirs have valid cached primary Sentinel-2 estimates: KRS, Bhadra, Tungabhadra, Supa, Vani Vilasa Sagara and Varahi. The five-reservoir repair audit is in output/processing-repair-report.md. Newer cloudy scenes were rejected, with rejection reasons in provenance. Primary concentration, dates, raster, map, RGB and EPA classification share acquisition metadata. A scene with unusable chlorophyll can retain RGB and an unavailable concentration. Sentinel-3 is accessible only as a separately labelled comparison, never a primary fallback.

The experimental Gilerson retrieval applies an aquatic-reflectance equation to provider Sen2Cor L2A BOA reflectance. This is an approximation, not locally calibrated or ACOLITE corrected. Project-specific QC uses water SCL, cloud/shadow exclusion, 60 m interior/cloud buffers, positive finite reflectance, minimum 25 pixels/10% reservoir coverage and conservative 1–100 µg/L output screening. Aggregation is median. Concentration screening can bias retained spatial samples; inspect valid coverage. NDCI remains dimensionless and is never presented as concentration.

Satellite-derived chlorophyll-a estimates have not yet been validated against Karnataka field measurements.

Deferred: expanding to 100 sites, verifying the 23 new water polygons, full ACOLITE processing and field calibration/accuracy. Existing training APIs remain available but model evaluation, dominance and monthly-analysis UI are not shown. No synthetic observations were added.

See THIRD_PARTY_NOTICES.md for repository audit and sources. Use “Refresh Sentinel-2 estimate” for on-demand processing of mapped sites; cached results are restored on page visits; manual refresh searches again. Missing sites and failed scenes remain explicit; no silent substitution.
