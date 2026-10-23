# Karnataka historical FAI acquisition — in progress

Status: 23 October 2026. This is a progress report, not a completed historical coverage or ML-feasibility claim.

The inventory remains exactly the existing 46 records in `data/reservoirs.json`. Its SHA256 is recorded in `data/fai-history/manifest.json` and checked against the current file.

Catalogue searches completed for all 46 polygons for 1 January 2022–22 October 2026 inclusive (the acquisition run's frozen cutoff). They returned **18,945 deduplicated acquisition candidates**. A candidate is not a usable observation. Full saved catalogue pages and per-reservoir scene counts are under `data/fai-history/<id>/catalogue/` and `catalogue-summary.json`.

Pixel extraction is ongoing. Run ` .venv/bin/python research/fai-history/summarize.py ` from the repository to refresh `progress.json`, `reservoir-counts.csv`, `fai-time-series.csv` and `forecast-pairs.csv`. These files are snapshots and remain incomplete until `run_complete` is true and remaining download errors are resolved or explicitly reported.

The reader extracts actual SCL, B04, B08 and B11 on a common 60 m grid. It applies SCL water, cloud/shadow dilation, shoreline erosion, reflectance validity, ≥25 pixels and ≥10% coverage, and ≥95% scene footprint. Same-pass mosaics are supported; overlapping acquisitions are deduplicated. FAI is dimensionless. Valid output NPZs preserve SCL and masks, including newly processed Varahi history. Existing Varahi operational cache is not overwritten.

Temporary raster errors are retained with explicit reasons and retried on resume. The resumed reader refreshes signed-access tokens on transport failures and uses bounded retries. Genuine mask/coverage rejections are cached. Do not count transport failures as proof of unavailable clear imagery. Catalogue checkpoints, successful arrays and completed result metadata survive interruption; result JSON writes are atomic.

The 10-day exploratory target uses a valid future acquisition 7–13 days later, selected closest to ten days. No observations or labels are interpolated. The future observation date is a label definition, not an available input feature. Chronological split dates, purging and repeated-target grouping must be established after the full history is available. No training or evaluation results exist yet.

The ML data gate is **pending**, not failed: processing remains unfinished. Dashboard integration is also pending. Current new implementation consists only of acquisition, QC, FAI calculation, persistence and dataset summarization. Existing chlorophyll and dashboard components remain separate and unchanged.
