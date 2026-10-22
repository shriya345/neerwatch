# Genuine data and service setup

## NASA SeaBASS CAML: current active training source

The user supplied `CAML_cyanobacteria_abundance_20211229_R1.sb` from Downloads. The original is preserved in `data/caml/`, and all 23,570 records are parsed with source header, units, missing-value handling and a SHA-256 audit. No competition split is present or fabricated.

**The abundance unit declaration is inconsistent with the supplied severity classes.** The current models use only source-provided categorical severity; numerical density conversion/regression is disabled. See [CAML audit](CAML_DATA_AUDIT.md).

```sh
.venv/bin/python -m pipeline.seabass /absolute/path/to/CAML_cyanobacteria_abundance_20211229_R1.sb
.venv/bin/python -m pipeline.caml_prepare --per-class 75 --workers 4
.venv/bin/python -m pipeline.train --epochs 150
```

The actual initial cohort selected 342 class-enriched records and obtained 135 quality-approved historical matches. This supports a small, weak-performing research classifier, not operational monitoring accuracy. Real test results are in `models/metadata.json` and the dashboard.

Official open-data release and use/citation instructions:
https://www.drivendata.org/competitions/143/tick-tick-bloom/page/879/

Source DOI: https://doi.org/10.5067/SeaBASS/CAML/DATA001

For a separate original-competition CSV workflow, obtain actual `train_labels.csv` and `metadata.csv` from the official challenge; do not invent them from CAML or assume its original competition partitions are recoverable. CAML is already sufficient for the current provided-category experiment.

## Sentinel-2 and weather

Planetary Computer STAC and public imagery signing use no account credentials. Raster assets are read by range requests; access may be throttled. A container-level SAS token is cached only in process memory. SAS credentials are not written into observation metadata.

NASA POWER daily meteorology uses public access. Missing values (`-999`) become null. The dashboard displays actual observation dates, never the retrieval date as a measurement date. Air temperature is not lake-water temperature. POWER data are gridded reanalysis/model products, not reservoir instruments.

## Copernicus CLMS chlorophyll-a

1. Register/sign in to https://dataspace.copernicus.eu/ yourself.
2. Open the Copernicus Data Space Sentinel Hub dashboard and create an OAuth client for API access.
3. Set these environment variables in the backend terminal, never in React or source control:

```sh
export CDSE_CLIENT_ID='your-client-id'
export CDSE_CLIENT_SECRET='your-client-secret'
```

4. Run a completed nominal composite query:

```sh
.venv/bin/python -m pipeline.clms --reservoir bhadra --period-start 2026-09-01
```

The adapter uses the documented BYOC collection `5c2c9b2c-2893-41d9-b2bc-fbd6e5b8b31d`, a single nominal day selector, 300 m grid, nearest resampling, and bands CHLAMEAN/CHLAUNC/FCBPROB/QFLAG/NOBS/dataMask. It retains the TIFF and a quality summary in `data/cache/clms/`. A nominal date represents a full 10-day composite (the final dekad extends to month end), not a daily concentration.

**Provider quality review is required before publishing concentrations.** The collection documentation does not give numeric QFLAG bit mappings. The reviewed v2.0 manual says flags summarize why individual inputs were removed and do not automatically indicate degradation of the final composite. It also notes possible unremoved adjacency contamination. Do not guess that every nonzero flag is invalid, or guess a flag bit order.

After verifying the actual product's numeric flag metadata and corresponding manual/version, create `data/clms-quality-policy.json` with `accepted_qflags` (a numeric list justified by the metadata), `provider_manual_url` (an actual Copernicus manual URL), `max_relative_uncertainty_percent`, `min_pixels`, and `min_coverage`. These acceptance settings are explicit project quality-screening choices, not universal provider thresholds. No default policy or invented bit mapping is supplied. The adapter will otherwise retain raw retrievals in `pending_provider_flag_review` state and leave the concentration dashboard unavailable.

Documented source:
https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/clms/bio-geophysical-parameters/water-bodies/lake-water-quality/lwq-nrt_global_300m_10daily_v2.html

Reviewed manual:
https://land.copernicus.eu/en/technical-library/product-user-manual-lake-water-quality-v2

The reviewed v2.0 manual describes chlorophyll and floating cyanobacteria as demonstration variables pending review. Check the actual delivered product/version before presenting them. FCBPROB does not establish field cyanobacteria dominance. Publication time has not been verified; this adapter's output is not eligible for training a leakage-free forecast without that additional timing check. OAuth/process requests could not be exercised without credentials; this path is implemented but unverified end to end.

## Import existing genuine chlorophyll observations

```sh
.venv/bin/python -m pipeline.import_chlorophyll /absolute/path/to/real-chlorophyll.csv
```

Required header (no invented sample rows are provided):

```csv
reservoir_id,observed_at,chlorophyll_a,unit,source,source_url,method,quality_status,cyanobacteria_dominance_established,dominance_evidence_url
```

- `reservoir_id`: one of the IDs in `data/reservoirs.json`.
- `observed_at`: actual measurement/observation time; no future dates.
- `chlorophyll_a`: finite concentration, 0 to below 10000.
- `unit`: `µg/L`, `ug/L`, `mg/m³` or `mg/m3` (numerically equivalent).
- `source_url`: HTTPS URL of the real source; `source` and `method` required.
- `quality_status`: `approved`, only after actual source quality review.
- `cyanobacteria_dominance_established`: `true` only with separate evidence.
- `dominance_evidence_url`: HTTPS evidence URL required when dominance is true.

The importer validates schema, dates, units and provenance fields. It cannot independently authenticate the scientific validity of a supplied source or dominance statement; that remains an evidence-review step. Preserve the underlying source data.
