# NEERWATCH: fixed 46-reservoir FAI and mandatory ML plan

22 October 2026. Scope is exactly `data/reservoirs.json`: no reservoir additions, deletions, renaming or international matching campaign. No application modifications or training performed in this assessment.

## Current evidence and decision

Fresh inspection confirms 46 reservoirs and 92 accepted Sentinel-2 history records, two per reservoir. FAI was recalculated from the actual saved B04/B08/B11 arrays for every record. The accompanying `current-46-reservoir-audit.json` lists every existing name, scene ID, acquisition date, source URL, valid-pixel count, valid fraction, FAI value and metadata/mask status.

45 reservoirs / 90 observations have saved SCL permitting water-mask reconstruction. Varahi's two observations (9 and 12 October 2026) have a saved accepted mask but no SCL: their numerical FAI is reproducible only under that saved mask. Do not call their full QC independently reproducible. Minimum observed FAI support is 27 pixels and 11.60% of polygon pixels; all recalculated records exceed existing 25-pixel/10% thresholds under their respective masks. These thresholds are project screening, not independent water-quality validation.

**Indicator: technically feasible for 45 reservoirs with fully reconstructable saved masks; Varahi requires repair or an explicit QC limitation. Mandatory ML: not currently feasible from the confirmed Karnataka time series. Stop before application integration under the user's conditional instruction.** This is not permission to omit the ML requirement from the final project.

## Fixed reservoir inventory

KRS; Bhadra; Tungabhadra; Supa; Varahi; Vani Vilasa Sagara; Kabini; Harangi; Hemavathi; Almatti; Linganamakki; Markonahalli; Yagachi; Hidkal; Nugu; Kadra; Basava Sagara; Malaprabha (Renuka Sagara); Gerusoppa; Kodasalli; Karanja; Kanva; Manchanabele; Suvarnavathy; Taraka; Votehole; Bennethora; Chandrampalli; Dharma; Upper Tunga; Chikkahole; Chiklihole; Hattikuni; Narihalla; Upper Mullamari; Lower Mullamari; Gundal; Gandorinala; Maskinala; Chulkinala; Harinala; Hirehalla; Uduthorehalla; Jambhadhahalla; Tattihalla; Savehaklu.

## Second-indicator integration plan

1. Retain current chlorophyll calculations, dates, history, citations, category logic and dashboard controls. Compute FAI alongside each existing Sentinel-2 processing result, using the same real acquisition and polygon; preserve six-band source/scale/offset manifests and SCL. Do not substitute another reservoir's result.
2. Use `B08 − [B04 + (B11−B04) × (842−665)/(1610−665)]`, median of accepted pixel residuals. This is a dimensionless spectral index, not µg/L or measured biomass. Store independent FAI pixel count, valid fraction, processing version and mask provenance. Do not condition FAI acceptance on the Gilerson chlorophyll range filter.
3. Use a consistent FAI mask: SCL water=6, one 60 m water-edge erosion, one-pixel dilation of shadow/cloud/cirrus classes 3/8/9/10, finite positive ≤1 reflectance in the three required bands. Recompute historical values consistently before showing trends. Quality flags are project screening outcomes derived from SCL, not a biological validation flag.
4. For Varahi, retrieve original SCL for the exact two scene IDs recorded in the audit, align to the saved grid, and recompute with preserved scaling metadata. If retrieval or alignment fails, retain Varahi in the website and show “FAI historical QC incomplete”; do not silently use its legacy mask as equivalent verified QC. No repair was attempted in this planning pass.
5. Add a compact “Floating Algae Index (FAI)” panel beside chlorophyll with acquisition date, dimensionless value and quality status. Describe it as a satellite indicator of surface optical conditions associated with floating algae. Show absolute index change between compatible dates, not percentage change near zero. No WHO/EPA concentration category applies to FAI. Retain all current source citations and add FAI method plus Sentinel-2 scene attribution.
6. Explain that floating vegetation, sediment, shoreline mixtures, adjacency/glint and correction errors can affect FAI. A median can miss localized surface patches; SCL water-only masking can reject thick scum. Negative values are legitimate. No species or toxicity inference.

Scientific basis: [Hu (2009), FAI](https://doi.org/10.1016/j.rse.2009.05.012). Sentinel-2 wavelengths and the reservoir QC are the project's adaptation, not a locally field-calibrated biomass algorithm.

## Mandatory trained regression: exact blocker and viable target

A genuine, relevant target is **future satellite-observed FAI** at a prespecified horizon, using past FAI/reflectance, season and available past meteorology. Future observed FAI is a legitimate numerical satellite-proxy target. It is not independent measured biomass. Calculating FAI from same-date bands and training a model to repeat that equation would add no demonstrated predictive skill and must not be presented as validated algal estimation.

Confirmed consistent history gives only **45 one-step transitions after excluding Varahi**, zero two-lag training examples, and no adequate per-reservoir chronological train/validation/test sequence. Earlier sparse feature records increased candidate reservoir-days to 104, but they were not harmonized and cannot resolve the short-history problem. Existing weather alignment is incomplete. Independent PC labels remain unavailable. The international GLORIA subset does not establish Karnataka accuracy or a second-indicator model; it is background evidence, not the primary objective.

The blocker is therefore **insufficient consistently processed temporal labels across the fixed Karnataka reservoirs and seasons**, not lack of an ML library or a requirement for synthetic labels.

## Next bounded feasibility work before training

Acquire historical Sentinel-2 observations only for these 46 polygons, preferably covering multiple complete seasonal cycles. This is an acquisition target, not a claim that sufficient clear scenes exist. Cache catalogue and raster provenance, process every accepted acquisition consistently, deduplicate same-pass tiles, and record exclusions. Establish per-reservoir counts and fixed-horizon target pairs; never interpolate missing target labels to increase the count. Resolve Varahi. Align rainfall/temperature with explicit data-availability lag and missingness checks.

Preferred first experiment once enough independent dates exist: RandomForestRegressor, with XGBoost only as a challenger. Predict FAI at a declared 10-day horizon using a fixed ±3-day observation tolerance as an initial research protocol, not an optimized clinical threshold. Inputs must be available at issue time; no future imagery or realized future weather. Baseline: persistence, predicted FAI equals last observed FAI.

Use global chronological training/validation/test boundaries, purge target windows crossing boundaries and keep shared scene/date observations together. Tune only inside training folds. Add held-out-reservoir analysis for geographic transfer; report unsupported reservoirs. Report actual held-out MAE, RMSE and R², persistence skill and reservoir/season sample counts. Avoid MAPE for zero/negative FAI. Insufficient dates/groups means NO-GO, not fabricated metrics.

Related research supports baseline-controlled algae forecasting, not the current two-date dataset: [long-term algae RF forecasting](https://doi.org/10.1016/j.jenvman.2024.123478). [Sentinel-2 FAI/RF/XGBoost mapping research](https://doi.org/10.1007/s00477-023-02648-1) concerns contemporaneous classification and must not be cited as proof of future-FAI regression performance.

## Conditional completion criteria

Only after the data gate passes: train and evaluate reproducibly, save actual model/configuration/provenance, then integrate two distinctly labelled outputs: **observed satellite FAI** and **ML-predicted future FAI**. Keep empirical chlorophyll as a separate existing output. Show no prediction for unsupported inputs or horizons. Run backend/build checks and real end-to-end reservoir displays without changing the inventory.

Current status: FAI integration plan confirmed technically with the stated Varahi exception; trained ML feasibility not confirmed. No dashboard/model changes made. The mandatory combined deliverable is not yet complete.
