# NEERWATCH — Sentinel-2 monitoring update

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for the current startup steps, tested features, data counts and scientific limits. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the reuse audit.

The previous project documentation below is retained for provenance; its old dashboard descriptions do not describe the current primary Sentinel-2 interface.

---

# Karnataka Reservoir Algal Bloom Early Warning and Monitoring System

A **new** React + FastAPI project. No application code, models, synthetic data or configuration from the previous HAB project is used. With explicit user permission, original Copernicus rasters and their source metadata were verified and reprocessed.

## Start the working application

A local environment and production frontend have been prepared in this folder. From this project directory:

```sh
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

Open **http://127.0.0.1:8010/**. API documentation: **http://127.0.0.1:8010/docs**.

For a fresh machine (Python 3.11 or newer and Node.js 22.12 or newer):

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

For frontend development, run the API above and, in a second terminal:

```sh
npm --prefix frontend run dev
```

The development dashboard runs at **http://127.0.0.1:5180/** and proxies `/api` to port 8010. The API serves the production frontend when `frontend/dist` exists. Rebuild and restart the API after frontend changes.

## Current dashboard: observed chlorophyll monitoring

Expanded to 17 reservoirs: Shanti Sagara, Markonahalli, Yagachi, Malaprabha (Renuka Sagara) and Hidkal each have two real screened Sentinel-3 CHL_NN estimates. Monthly analysis and the separate cyanobacteria-dominance status row have been removed. WHO applicability is retained only in the reference context.

- Seventeen Karnataka reservoirs with sourced OpenStreetMap water polygons.
- Real satellite chlorophyll concentrations, dated earlier/latest comparisons, absolute and percentage changes, and review-required/not-required decisions. No forecasting interface.
- KRS, Bhadra, Tungabhadra and Supa: 247 provisional CLMS OLCI 300 m ten-day estimates, September 2024–September 2026.
- Kabini, Harangi, Hemavathi, Almatti, Basava Sagara, Linganamakki, Varahi and Vani Vilasa Sagara: two screened official Sentinel-3 CHL_NN observations each. Latest dates found are February 2026; earlier dates are retained explicitly.
- Official NetCDF units/packing are verified before conversion from log10(mg/m³) to µg/L. Source MD5s, quality flag definitions, geolocation and screened pixel extracts are preserved. No guessed chlorophyll conversion from Sentinel-2 indices.
- WHO historical 1999/2003 recreational-water reference values (10/50 µg/L), with the requested captions beneath each value. No cyanobacteria category or model evaluation/readiness section on the dashboard.
- Change-triggered review is the requested trend rule, not a WHO percentage-change rule. A value at or above a WHO reference prompts review/confirmation of cyanobacteria dominance even if decreasing. Without dominance, only a numeric comparison is made, not a WHO health determination.
- All-reservoir comparison table, genuine Sentinel-2 imagery, NASA POWER weather context and matching PDF reports.

Reproduce the public satellite acquisition:

```sh
.venv/bin/python -m pipeline.sentinel3_chlorophyll --limit 30 --observations 2
```

Full source NetCDF files are cached under `data/cache/sentinel3/` (excluded from the source ZIP). Source links, checked MD5s, acquisition/rejection audits and compact native-pixel extracts are included. See [the chlorophyll update](docs/CHLOROPHYLL_UPDATE.md).

## NASA SeaBASS CAML training (now completed)

The supplied Downloads file was parsed into **23,570 genuine field-label records**. It contains source-provided `severity` categories and **no original competition split**. The raw `abun` header declares cells/L but conflicts with the supplied categories; no corrected density or rederived labels are asserted. See [the full data/unit audit](docs/CAML_DATA_AUDIT.md).

A disclosed initial acquisition pilot selected 342 class-enriched records from 4,028 eligible 2018+ near-water records. **135** had genuinely aligned, quality-approved Sentinel-2 features. The final split is **70 training / 24 validation / 41 fixed geographic test** records, with all five classes represented in each partition.

| Model | Test accuracy | Macro F1 | Macro precision | Macro recall |
|---|---:|---:|---:|---:|
| Neural network | 26.83% | 0.2055 | 0.1562 | 0.3067 |
| Random Forest | 26.83% | 0.2662 | 0.2915 | 0.3133 |

**Performance is weak.** These are class-enriched pilot scores, not full-CAML population accuracy or Karnataka validation. These legacy research category estimates are not displayed on the dashboard and do not drive the chlorophyll review. The active interface uses observed chlorophyll comparisons.

Reproduce ingestion, cached satellite acquisition and training:

```sh
.venv/bin/python -m pipeline.seabass /absolute/path/to/CAML_cyanobacteria_abundance_20211229_R1.sb
.venv/bin/python -m pipeline.caml_prepare --per-class 75 --workers 4
.venv/bin/python -m pipeline.train --epochs 150
```

The supplied original is preserved under `data/caml/`. Its SHA-256, header, units, actual class counts and discrepancy audit are in `data/caml/audit.json`. No generated labels or missing feature imputation are used. CAML satellite matches are strictly before the sample calendar date and no more than ten days earlier, avoiding ambiguous source times.

The source's supplied categories are used directly; `abun`, region, provider, distance-to-water and source category are never predictor features. Only band statistics and NDCI/NDWI/FAI enter the model. The scaler is fitted on training records only. The final validation partition was repaired for class coverage using development-only counts; fixed test UIDs were preserved. The audit, including the initial evaluation, is in `reports/caml_split_audit.json`.

Artifacts are saved in `models/`: both models, scaler, metadata/input hashes, split manifest, genuine held-out predictions and confusion matrices. The dashboard exposes the actual evaluation, per-class statistics, both reservoir category estimates and model agreement. Restart the API after training; the production dashboard reads the saved artifacts.

To retry source failures in the same acquisition cohort, add `--retry-failed` to `pipeline.caml_prepare`. Increasing `--per-class` creates a larger documented cohort and requires a new evaluation; do not present the existing 135-record metrics as full-dataset results.

The older competition CSV workflow remains supported when CAML is not the active source. CAML ingestion is the current default; do not fabricate `train_labels.csv`, `metadata.csv` or a competition split from it.

## Refresh reservoir observations

```sh
.venv/bin/python -m pipeline.collect --reservoir priority --months 3
.venv/bin/python -m pipeline.collect --reservoir extended --months 1
.venv/bin/python -m pipeline.collect --reservoir bhadra --months 6
```

Each requested historical window ends seven days before the run date, then at 30-day intervals. Up to 20 prior days are searched per reservoir window. Training uses a stricter 10-day historical lookback. These are sparse historical samples, not complete daily coverage. Existing files keep real timestamps, source item IDs, quality counts and retrieval failures.

## Chlorophyll-a setup

See [data setup](docs/DATA_SETUP.md). Sentinel-2 NDCI is **not** silently converted into a concentration. No uncalibrated polynomial is presented as a measurement.

- Use Copernicus Data Space credentials for the CLMS adapter.
- Retain and inspect provider quality flags before publishing concentrations.
- Alternatively import genuine, documented chlorophyll observations with the strict CSV importer.
- Only comparable concentrations support change calculations. A validated seven-day chlorophyll forecast is not currently available.

## Verify

```sh
.venv/bin/python -m pytest -q
npm --prefix frontend run build
```

Tests check official density boundaries, invalid inputs, no invented predictions, all mapped geometries, genuine observation provenance, quality gates, monthly counts, exact captions, API errors and PDF generation. They do not manufacture training data to report an artificial score.

## Sources, attribution and limitations

The untouched reference notebooks are in `reference/`, cloned from [Ioannis Nasios / HarmfulAlgalBloomDetection](https://github.com/IoannisNasios/HarmfulAlgalBloomDetection), commit `1d127630b0678589c5bd2e257b7c289f686956cb`. See [reference audit and attribution](docs/REFERENCE_AUDIT.md).

The new implementation adapts the reference's methodology rather than copying its trained outputs. The original repository has no explicit licence file at the inspected commit; its notebooks are retained locally for research, with original attribution, and are not incorporated into the website bundle. Confirm upstream reuse terms before redistributing its source.

Read [methodology](docs/METHODOLOGY.md), [architecture](docs/ARCHITECTURE.md), [results and limitations](docs/RESULTS.md), and [demo guide](docs/DEMO_GUIDE.md).

Field labels come from the **United States**, not Karnataka. Evaluation there cannot establish Karnataka field accuracy. Satellite reflectance, chlorophyll-a estimates, cyanobacteria field density, dominance evidence, and toxin concentrations are distinct quantities. Historical WHO guidance is contextual, not a Karnataka regulatory limit. Neither routine monitoring nor any model output certifies drinking-water safety.

The application is prepared for local use. It has not been deployed or connected to the old repository or Vercel website.
