# CAML ingestion, units and training audit

Source: NASA SeaBASS CAML, DOI https://doi.org/10.5067/SeaBASS/CAML/DATA001 .
Official archive: https://seabass.gsfc.nasa.gov/archive/NASA_HEADQUARTERS/SGupta/CAML/CAML_2013_2021/archive .
Official open-data release: https://www.drivendata.org/competitions/143/tick-tick-bloom/page/879/ .

Citation: S. Gupta, E. Gelbart, R. Gupta, K. Wetstone and E. Dorne (2024). *Cyanobacteria Aggregated Manual Labels Dataset (NASA and DrivenData).* SeaBASS. DOI 10.5067/SeaBASS/CAML/DATA001.

## Actual supplied file

Located in Downloads as `0c233b5a95_CAML_cyanobacteria_abundance_20211229_R1.sb`. The original bytes are preserved in `data/caml/CAML_cyanobacteria_abundance_20211229_R1.sb`.

SHA-256: `ca8660ec930dde57f38ec20f89eb0e6e528d3917f96fbae79193f0bed2cb5f22`.

The archive's filename matches the supplied file. An unauthenticated direct file download returned Earthdata Login HTML, not dataset bytes; byte-for-byte equivalence with a fresh server copy was therefore **not independently verified**. No login HTML was treated as data. The documentation tarball is linked from the parent directory but also requires authenticated download. The PDF named in the file header was not available in the public `documents/` listing. No claim is made that an unavailable manual resolved the unit issue.

## Schema verified from the file

| Field | Declared unit | Treatment |
|---|---|---|
| uid | none | Original unique sample ID; validated, not replaced |
| data_provider | none | Original provider retained as provenance; not a predictor |
| region | none | Original region retained; not a predictor |
| lat, lon | degrees | Original sample coordinates; range checked |
| date | yyyymmdd | Strict calendar parsing; normalized in derived CSV |
| time | hh:mm:ss | Original supplied time retained; not assumed to be a precise sampling time |
| abun | cells/L | Original numerical values preserved; inconsistent with supplied severity classes after literal physical conversion |
| severity | none | Supplied integer categories 1–5; used as the classification target without rederivation |
| distance_to_water_m | m | Original positional screening value; one literal `NA` preserved as missing |

There are **23,570 records**, **12,681 unique coordinate pairs**, and no duplicate UIDs. Dates span **2013-01-04 to 2021-12-29**. The categorical class counts are 9,761 / 4,083 / 3,812 / 5,824 / 90 for classes 1–5.

The header declares `missing=-9999`, while one distance field also contains the literal `NA`. Both are treated as missing, never filled. Measurement depth is not used: its metadata and comments contain a placeholder/inconsistency and comprehensive source depth information was unavailable. No depth, coordinates, dates, measurements or competition partitions are invented.

## Abundance inconsistency: no guessed conversion

The header declares `abun` in **cells/L**. The physical conversion to cells/mL is therefore **abun / 1000**. Applying that conversion and the documented severity boundaries disagrees with **13,809 of 23,570** supplied classes.

For a diagnostic only, multiplying raw `abun` by 1000 reproduces all supplied categories. That arithmetic agreement **does not establish the correct physical unit** and is not accepted as a correction. It could reflect an upstream unit/scaling problem; source-author clarification or authoritative corrected documentation is needed.

For example, UID `aabm` retains its actual raw `abun=0.585` and supplied `severity=1`. Neither value is replaced. The original challenge's documentation separately describes a measured 585 cells/mL for this UID, reinforcing the discrepancy rather than resolving the file's declared unit.

Decision: **train on the genuine, source-provided `severity` categories; do not derive labels from `abun`, assert corrected density, fit density regression or display numerical cell-density estimates.** Abundance is not an input feature. The unit issue is retained in model metadata, the dashboard and PDF reports.

## Actual feature-acquisition cohort

The initial reproducible acquisition pilot screens for:

- Samples from 2018 onwards, within the mature historical Sentinel-2 L2A period.
- A nonmissing source-reported distance to water of at most 100 m. This is a screening aid, not a guarantee of surveyed coordinate accuracy.
- A fixed-seed random cap of 75 records per supplied severity class. There are only 42 eligible class-5 records, so **342 records** were selected from **4,028 eligible** records.

This is deliberate class enrichment for an initial acquisition pilot. It changes class prevalence. Subsequent metrics describe the selected, quality-approved subset and must not be presented as full-CAML population performance or as an unbiased estimate of operational accuracy.

Each selected record is queried at its original coordinates within a 400 m radius box. Features summarize only valid water interior pixels in that box, not necessarily the exact parcel sampled in the field. Imagery must be **strictly before the sample calendar date and no more than ten days earlier**; this conservative rule avoids using potentially later same-day imagery when source times are ambiguous. No future acquisitions or generated feature values are used.

All existing quality rules remain: polygon clipping, SCL water, cloud/shadow exclusion, 60 m shoreline/cloud buffers, valid reflectances, at least 25 valid water pixels and at least 10% valid coverage. Reading SCL first rejects unusable areas early without weakening these rules.

**135 records passed**, with class counts **38 / 33 / 25 / 19 / 20**. The remaining **207** selected records are rejected/unavailable; they are not imputed or converted into measurements. Features are only the 21 band-statistic/index fields listed in `pipeline/features.py`. Source categories, abundance, provider, region and distance-to-water are excluded from predictor inputs.

Manifests:

- `data/caml/audit.json`: source schema, units, missing values, source hash and discrepancy audit.
- `data/caml/labels.csv`: parsed real records with source categories and no fabricated split/density column.
- `data/caml/acquisition_selection.json`: selection rules, seed, all chosen UIDs and class counts.
- `data/training_features.csv`: 135 genuine aligned feature rows with dates, original coordinates and STAC source URLs.
- `data/training_acquisition_summary.json`: accepted counts and individual rejection reasons.

## New evaluation split

The `.sb` file has **no original competition split**. None is inferred from UID, region or source provider.

A fresh geographic grouping is created using KMeans on unique sample coordinates, then a fixed-seed geographic test partition. Validation is selected **only within the remaining development records**, using category coverage and target size, not model or test performance. Training and validation require at least two samples of every class. No geographic cluster is shared across partitions.

The first trial's validation partition omitted class 3. It was repaired within development data; the test UIDs were retained exactly. `reports/caml_split_audit.json` preserves the initial evaluation and the fixed-test audit. No model-performance-based split search was performed. The final sizes are **70 training / 24 validation / 41 fixed test**.

The scaler is fitted on training data only. Four MLP learning-rate/dropout candidates are selected on validation macro F1, with class-weighted loss, early stopping and a learning-rate scheduler. Random Forest uses the same training and test records. The final test values are reported even if weak; they are not claims of improvement over another population or Karnataka validation.

`models/test_predictions.csv` preserves genuine source categories and both models' held-out predictions. Tests recompute metrics from that table, check geographic separation, confirm that the scaler uses only training rows, and verify that no synthetic density or source split was created.

## Remaining scientific limitations

- Only 135 quality-selected records support this initial model. Test supports are small, and geographic clusters approximate waterbody separation.
- Labels have 2013–2021 US origin. These are not Karnataka field labels.
- Training site-box support differs from whole-reservoir polygon summaries used for Karnataka estimates.
- Source coordinates can be uncertain; nearest water and SCL screening do not prove a particular sampled lake or water parcel.
- Spectral quality rejection can preferentially exclude some conditions, including bright surface blooms.
- The unresolved abundance-unit declaration precludes numerical density claims.
- Accuracy and F1 from this pilot do not establish operational reliability. Karnataka predictions are exploratory same-date category estimates, never a validated seven-day forecast or toxicity determination.
