# Methodology

## Observations and provenance

Every displayed observation comes from a retrieved provider response or a documented real observation import. No synthetic labels, model outputs, concentrations, weather measurements or evaluation metrics are supplied. Boundary coordinates come from retrieved OpenStreetMap reservoir polygons, not hand-invented map points. OpenStreetMap is a mapped source and is not a surveyed field boundary; independent boundary verification remains appropriate before operational use.

The first four reservoirs are KRS, Bhadra, Tungabhadra and Supa. The registry also includes Kabini, Harangi, Hemavathi, Almatti, Basava Sagara, Linganamakki, Varahi (Mani Reservoir), and Vani Vilasa Sagara. Per-reservoir geometry provenance is in `data/boundaries/*.geojson` and `data/reservoirs.json`.

Public imagery: Copernicus Sentinel-2 L2A through Microsoft Planetary Computer STAC. Weather: NASA POWER daily gridded meteorology, including air temperature, precipitation and wind. Collection dates, retrieval timestamps, STAC item IDs, native spatial scales, query end dates and quality flags/counts are retained.

## Satellite preprocessing

- Mapped reservoir polygons are transformed to a local UTM grid.
- Six bands (B02, B03, B04, B05, B08, B11) and scene classification are aligned to one 60 m screening grid by nearest-neighbor resampling.
- Native DN scale and offset are applied. For Sentinel-2 processing baseline 04.00 or later, the native BOA offset is -1000 DN with a 10000 quantification factor when the asset does not expose scale/offset metadata. Zero/no-data pixels are excluded. This is native Planetary Computer imagery, not the already harmonized Earth Engine collection.
- SCL class 6 supplies the water mask inside the mapped polygon. SCL classes 3, 8, 9 and 10 exclude shadow, cloud and cirrus, with a one-grid-cell cloud buffer.
- A one-grid-cell (60 m) water erosion reduces shoreline mixed pixels. SCL water omission can also remove bright surface blooms; the mask is conservative and may bias coverage.
- All six band reflectances must be finite and in (0, 1]. Negative or saturated values are rejected rather than clipped into valid data.
- A sample requires at least 25 valid water pixels and 10% valid polygon coverage. These are explicit project screening choices; their scientific suitability is not independently calibrated. Coverage is always shown, and limited coverage must not be taken as a complete reservoir mean.
- Accepted bands are summarized by mean, median and standard deviation. Spectral indices use valid water pixels only.

NDCI = (B05 - B04)/(B05 + B04).
NDWI = (B03 - B08)/(B03 + B08).
FAI = B08 - [B04 + (B11 - B04) × (842 - 665)/(1610 - 665)].

Wavelengths are nominal nanometres. NDCI/NDWI are normalized indices; FAI is a reflectance residual. None is a laboratory cell count or a chlorophyll concentration. Sentinel-2 L2A atmospheric correction is not a dedicated validated aquatic correction. No calibration for these reservoirs has been established.

## Field-label alignment and supervised task

The genuine DrivenData labels are manually collected, laboratory-analyzed cyanobacteria densities from the **continental United States**, dating back to 2013. They were not collected in Karnataka. The data description is https://www.drivendata.org/competitions/143/tick-tick-bloom/page/650/ .

The initial supervised task is **same-date five-class severity classification**. Each sample joins by UID to its actual location and date. A 400 m local sample-site box is queried for Sentinel-2 imagery no more than ten days before the label date, including that calendar date. SCL water interiors are used. This point-site training extraction and reservoir-polygon inference differ in spatial support; this is an additional transfer limitation.

The training validator rejects future imagery, windows older than ten days, coordinate disagreement, duplicate sample IDs, nonfinite inputs, absent provenance, incorrect density-class mappings and non-training metadata rows. Older samples without Sentinel-2 L2A coverage remain unavailable; Landsat support is not implemented. NASA POWER weather is currently context only, so no weather imputation enters the classifier.

## Neural network and baseline

Features are only the valid-water band statistics and three spectral indices. Coordinates, raw density and severity are not included as predictor features. All five classes must appear in the training split.

Spatial holdout: KMeans groups sample coordinates into up to twenty geographic clusters, followed by group-disjoint train/validation/test partitions of approximately 60/20/20. Ratios vary by cluster sizes. Geographic clusters are an approximation; independent waterbody identifiers would provide stronger isolation, and adjacent sites across a cluster boundary can remain correlated.

A StandardScaler is fitted on training features only. The PyTorch MLP is `input → 64 ReLU → dropout → 32 ReLU → dropout → 5 logits`. Training uses class-weighted cross entropy, AdamW, a validation-driven learning-rate scheduler, early stopping after 15 unimproved epochs and a maximum of 150 epochs. Candidate learning rates (0.001, 0.0003) and dropout rates (0.15, 0.30) are selected using validation macro F1. The test set is not used to choose the candidate.

A 300-tree Random Forest with balanced class weighting is trained on the same training partition and evaluated on exactly the same test samples. Evaluation records accuracy, macro F1, precision, recall, per-class support, confusion matrices and baseline comparison. Input hashes and a UID-level split manifest are saved. No model or score is included while genuine data are missing.

Maximum softmax probability is labelled as **uncalibrated**, not interpreted as verified probability of correctness. Karnataka estimates, if later enabled, remain explicitly unvalidated research outputs until matched Karnataka field measurements support validation.

## Chlorophyll-a, changes and monthly analysis

The dedicated CLMS adapter retrieves provider chlorophyll-a, uncertainty, floating-cyanobacteria probability, quality flags and observation count for completed 10-day composite periods. It requires OAuth credentials. Raw retrievals remain pending until an explicit provider-grounded quality policy is set. Quality flag bit order is not guessed from a list of names. The reviewed v2.0 manual places newly added chlorophyll and floating-cyanobacteria variables in demonstration status; the actual delivered version must be checked.

Concentrations may also be imported from genuine sources with actual dates, units, method and source provenance. µg/L and mg/m³ are numerically equivalent. Chlorophyll-a is not trained against cyanobacteria density labels.

Absolute and percentage change require consecutive comparable concentrations from the same method and source. Percentage change is unavailable when the earlier concentration is zero. Monthly summaries show actual observation-window coverage, missing acquisition windows, available chlorophyll means and available weather dates. Sparse windows are not daily coverage. Severity distributions are computed only after a genuine model is available.

## Monitoring interpretation

DrivenData density boundaries define five documented label classes; they are not universal health-safety limits. The website attaches the requested source caption directly under each range.

Historical WHO 1999/2003 guidance summarized on the EPA website supplies 10 and 50 µg/L chlorophyll-a context **only with cyanobacteria dominance**. The age and scope of that guidance are explicitly shown. These are not asserted to be current Karnataka regulations. Source: https://www.epa.gov/habs/world-health-organization-who-1999-guideline-values-cyanobacteria-freshwater . A 12 µg/L EPA chlorophyll health criterion was not verified and is not added as one.

Chlorophyll-based guidance requires independently documented dominance. Satellite floating-cyanobacteria probability and chlorophyll alone do not establish it. An independent >=50% rise in comparable recent chlorophyll observations can prompt increased monitoring under an explicitly **project-defined, uncalibrated** screening rule. This is separate from WHO/EPA guidance.

A 30-day freshness limit is a project rule for available water-quality evidence. With no recent accepted satellite or chlorophyll observation, the status is Insufficient data. Routine monitoring never means water is safe. No toxicity, drinking-water suitability or confirmed harmful bloom is inferred.

## Forecasting

No seven-day forecasting model has been trained or validated. The classifier is labelled same-date and has a zero-day horizon. CLMS composites are not daily labels; nominal-period dates are not necessarily publication times. A forecast requires properly later targets and proof that every input was available at the issue date. Sparse or publication-uncertain observations are insufficient for that claim. Historical analysis continues without a forecast.

## Meteorological sanity screening

The acquired NASA POWER responses contain several unusually high precipitation values. Original provider values and declared units are preserved. A project sanity screen excludes rainfall at or above 200 mm/day, air temperature outside -60 to below 60 °C, and wind outside 0 to below 100 m/s pending source review. These are project screening limits, not provider validation or proof that an extreme event did not occur. Monthly rainfall totals identify accepted dates and flagged exclusions, so they must not be interpreted as complete monthly precipitation when records are excluded.

## CAML update: actual completed training

The current experiment supersedes the earlier missing-CSV state. The full SeaBASS file contains 23,570 genuine records with supplied category labels and no competition split. Its cells/L abundance declaration conflicts with 13,809 source categories after literal physical conversion; no guessed correction or density regression is used. See `CAML_DATA_AUDIT.md` for the schema, units and full audit.

A class-enriched 342-record acquisition pilot obtained 135 valid historical satellite matchups, strictly before each sample calendar date and at most ten days earlier. The final locally generated geographic split is 70 training / 24 validation / 41 fixed test. Validation class coverage is selected using development data only; the original fixed test is unchanged. The scaler is fitted on training rows only. No provider, region, abundance or severity label enters the predictors.

Both models achieved 26.83% test accuracy. Neural-network macro F1 is 0.2055; Random Forest macro F1 is 0.2662. These weak pilot results do not establish operational reliability or Karnataka validation. Exploratory reservoir category estimates are shown, with class probabilities explicitly uncalibrated and model agreement disclosed. They are excluded from monitoring alerts. Source-provided categories are never relabelled as measured densities.
