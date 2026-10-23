# NEERWATCH: Satellite-Based Algal Indicator Monitoring for Karnataka Reservoirs

Authors: Shriya HR; Sudeeksha V; Shradha Kubhal; Sandya K
Department of Computer Science and Engineering, Dayananda Sagar College of Engineering, Bengaluru, Karnataka, India

Abstract—NEERWATCH is a web system for viewing dated satellite-derived algal indicators for 46 Karnataka reservoirs. Sentinel-2 Level-2A imagery is processed using reservoir boundaries, water and cloud masks, and quality checks. A Gilerson-based two-band expression provides experimental chlorophyll-a screening estimates, while a Sentinel-2 adaptation of the Floating Algae Index (FAI) provides a dimensionless surface-algae indicator. A separate workflow applies five original pretrained CyFi LightGBM regressors to reviewed satellite inputs to estimate cyanobacteria density. The implementation uses Python processing, file-based provenance, FastAPI services, and a React/Leaflet interface. In the inspected snapshot of 23 October 2026, the system stores 92 chlorophyll observations, 90 QC-approved FAI observations across 45 reservoirs, and experimental CyFi estimates for 32 reservoirs. Fourteen reservoirs remain unassessed by CyFi. Backend verification completed with 111 passing tests, and the frontend production build succeeded. These checks establish software behavior, not environmental accuracy. Independent Karnataka field validation is absent, and no future-FAI forecasting model is deployed.

Index Terms—Sentinel-2, chlorophyll-a, Floating Algae Index, LightGBM, cyanobacteria, reservoir monitoring.

## I. INTRODUCTION

Reservoir monitoring requires observations that can be traced to a place, time and method. Satellite imagery can cover several reservoirs, but clouds, mixed pixels and optical differences between waterbodies affect interpretation. A concentration estimated from an image is not equivalent to a laboratory measurement. A monitoring interface should make this difference visible.

NEERWATCH addresses this implementation problem for a fixed inventory of 46 Karnataka reservoirs. It combines dated chlorophyll-a estimates, observed FAI, original imagery, temporal comparison and experimental machine-learning estimates in one interface. The regional scope is a project choice; it does not imply that the methods have been calibrated for Karnataka.

The contribution is a working, traceable integration of established methods and a pretrained model. We do not propose a new chlorophyll retrieval equation, train a new cyanobacteria model, or report local predictive accuracy. The paper describes the code and stored snapshot inspected on 23 October 2026.

## II. SYSTEM ARCHITECTURE

The frontend uses React and Leaflet. It provides reservoir search, a map, comparison tables, image views, dated indicator cards and report links. FastAPI routes return reservoir metadata, processing status, indicator values and files. The frontend obtains results through HTTP requests to `/api` routes; the production build can be served from the same local application.

Python processing is separated into two paths, shown in Fig. 1. The chlorophyll/FAI path uses projected, scaled Sentinel-2 reflectance arrays. The CyFi path preserves the pretrained model's original crop and feature calculation. The model does not consume the displayed chlorophyll estimates as training labels or inputs.

[[FIGURE1]]

Storage is file-based. JSON records retain dates, scene identifiers, sources and QC information. NPZ files retain arrays; GeoTIFF files retain georeferenced chlorophyll maps; PNG files support display. A published FAI snapshot separates the dashboard from the unfinished historical acquisition job. CyFi results are cached against the input snapshot, model and worker code. Source and model checksums help identify accidental changes; they do not establish scientific accuracy.

The existing CSV and ReportLab PDF outputs remain separate from the experimental CyFi display. New CyFi values do not change the operational alert or report calculations. This separation avoids presenting an unvalidated model output as an official reservoir warning.

## III. SATELLITE PROCESSING AND INDICATORS

### A. Data selection and quality control

Sentinel-2 Level-2A data are obtained through Microsoft Planetary Computer scene metadata and raster assets. Reservoir polygons define the analysis area. The chlorophyll processor searches a bounded recent window, prefers newer suitable acquisitions and retains actual acquisition dates. Compatible same-pass tiles can be mosaicked; unrelated dates are not combined into a single observation.

For chlorophyll and the displayed FAI snapshot, arrays are aligned to a 60 m grid in the reservoir's UTM zone using nearest-neighbour resampling. Reflectance is derived from provider scale and offset metadata, with implemented baseline-dependent defaults. Raw zero values are treated as no-data. This is provider Sen2Cor bottom-of-atmosphere processing, not a locally validated aquatic atmospheric correction.

SCL class 6 identifies candidate water. The mask erodes the shoreline and buffers cloud/shadow classes 3, 8, 9 and 10 by approximately one 60 m analysis pixel. Scene footprint must cover at least 95% of the reservoir. At least 25 valid pixels and 10% polygon coverage are required. These are project screening gates; passing them does not prove a correct concentration.

### B. Chlorophyll-a screening estimate

The implementation adapts the Gilerson two-band relationship [1]. For retained pixels, it computes

C = [35.75(B05/B04) − 19.30]^1.124.                         (1)

B04 represents red reflectance near 665 nm and B05 red-edge reflectance near 705 nm. The positive-input and positive-base conditions are checked before use. Only finite estimates from 1 to 100 micrograms per litre are retained. Values outside that screening domain are rejected rather than clipped. The reported reservoir concentration is the median of accepted pixel estimates.

The original relationship and the operational band substitution are not identical measurement conditions. Atmospheric effects, suspended sediment, dissolved substances and reservoir-specific optics can bias the result. Therefore, the interface labels the result as experimental satellite-derived screening, not a field measurement.

For two compatible observations, absolute change is C_latest − C_earlier. Percentage change is 100(C_latest − C_earlier)/C_earlier when the denominator is valid. Both dates remain visible. Existing chlorophyll trophic screening uses implemented intervals of ≤2, >2–7, >7–30 and >30 micrograms per litre. These categories do not identify cyanotoxins.

### C. Observed Floating Algae Index

FAI measures a near-infrared departure from a red-to-shortwave-infrared baseline [2]. The implemented Sentinel-2 adaptation is

FAI = B08 − {B04 + (B11 − B04)(842 − 665)/(1610 − 665)}.   (2)

The nominal wavelengths are in nanometres. B08 is near infrared and B11 is shortwave infrared. FAI is dimensionless, and negative values are retained. It is distinct from the concentration estimate in (1), with no conversion to biomass mass or toxin concentration.

The snapshot builder reconstructs masks from saved SCL when available and applies finite-reflectance, pixel-count and coverage checks. Comparable history includes only QC-approved rows with the same method version. Varahi's two older FAI rows lack complete SCL provenance and are kept as legacy observations rather than included in the comparable trend. This limitation is independent of Varahi's newly approved CyFi input.

Sediment, aquatic vegetation and mixed pixels can influence FAI. Furthermore, water-only masking can remove dense surface scum. The system does not assign FAI severity or toxicity thresholds.

## IV. EXPERIMENTAL PRETRAINED CYANOBACTERIA ESTIMATION

### A. Model and project contribution

CyFi is an open-source tool for estimating cyanobacteria density from Sentinel-2 imagery [3]. NEERWATCH loads its five original saved LightGBM regression members. LightGBM is a gradient-boosted decision-tree method [4]. Regression produces a numerical estimate, unlike a classifier that directly selects a discrete label.

The upstream model was trained using field observations from the United States. We did not retrain it, create local training labels or claim new Karnataka evaluation scores. Our implementation verifies the model artifact, acquires genuine inputs, applies the original feature routine, checks quality, executes inference and exposes a dated experimental result. The numerical reference badge is assigned after regression by deterministic code.

### B. Inputs, QC and inference

The original CyFi input box extends 2 km from the reservoir point on each side. Native-grid assets include AOT, WVP, SCL and bands B01–B09, B11, B12 and B8A. Original raw digital-number preprocessing is retained, rather than replacing it with the separate 60 m chlorophyll arrays. This choice preserves software consistency but leaves radiometric transfer across processing baselines unresolved.

The feature vector has 30 ordered values: twelve spectral-band means; WVP and AOT means; water proportion; two green percentiles; five spectral ratios; four normalized-difference features; AOT range; month; days before sample; and land-cover class. The dated image-estimation workflow sets the sample-offset feature to zero without implying that a concurrent field sample exists. Land cover comes from the original 2020 C3S raster lookup.

Original cloud screening rejects a crop when SCL classes 7–10 occupy more than 5%. Original water-feature calculations are preserved, and all required features must be finite. An additional geographic check requires at least 95% of the crop's SCL water pixels to lie inside the intended reservoir polygon. Missing data, invalid registry points and rejected scenes do not generate a displayed prediction. No feature imputation, input clipping or undocumented scaling is used.

For model outputs z_1 through z_5 in log space, the original ensemble transformation is

D = round{exp[max(0, (z_1 + ... + z_5)/5)] − 1}.           (3)

D is displayed as estimated cells per millilitre. It is not a microscopy count or a validated whole-reservoir average. The application retains source dates, model version, file checksums, quality information and compatibility caveats. Finite inputs are not proof that values fall inside the training distribution. No local uncertainty interval or Karnataka accuracy is claimed.

### C. Display-only count reference bands

The four implemented bands are listed in Table I. The 20,000 and 100,000 values are drawn from the historical WHO-derived recreational framework summarized by EPA [5]. The cited source does not specify the 10-million cutoff; that split is explicitly a project display extension. Current WHO guidance uses additional indicators and evidence [6].

[[TABLE1]]

The labels are “Experimental cell-count reference bands.” Colors indicate numerical intervals, not safe/unsafe water, toxicity, legal compliance or confirmed health risk. Null, negative, nonfinite, withheld and incomplete values show “Not assessed.” Exactly 10,000,000 belongs to the High band. CyFi alone does not change operational alerts or PDF reports.

## V. IMPLEMENTATION RESULTS AND SOFTWARE VERIFICATION

The fixed inventory contains 46 reservoirs and 92 stored chlorophyll observations, two per reservoir. Latest chlorophyll estimates range from 16.18 to 67.65 micrograms per litre. Under the implemented screening intervals, 42 latest values are eutrophic and four hypereutrophic. These counts describe stored estimates, not a field survey.

The observed FAI snapshot contains 90 QC-approved observations across 45 reservoirs and two legacy Varahi observations. The completed first CyFi expansion pass increased experimental estimate coverage from eight to 32 reservoirs; 14 remain withheld. The original eight numerical estimates and their observations were preserved. Coverage is summarized in Fig. 2; different indicators have different eligibility conditions.

[[FIGURE2]]

Examples of unchanged CyFi estimates are KRS: 16,652 cells/mL, Bhadra: 16,710 cells/mL, and Supa: 7,105 cells/mL. KRS and Bhadra use 12 October 2026 acquisitions; Supa uses 20 October 2026. All three fall in the Lower count band. These are examples of numerical output, not evidence of true low biological risk.

The expansion reused cached acquisitions first, then searched genuine alternatives within 25 June–23 October 2026. The completed pass checked at most eight distinct dates per reservoir. Rejections and source metadata were checkpointed. This was a bounded search, not an exhaustive claim that no usable image exists for any withheld reservoir.

The backend test suite completed with 111 passing tests and one dependency deprecation warning. Tests check threshold boundaries, invalid values, provenance hashes, original-model execution, preservation of existing estimates, reservoir consistency and isolation from reports and alerts. The frontend production build succeeded. A live API check confirmed 46 entries, 32 complete CyFi results and 14 withheld results. Earlier browser checks covered example badges and missing-input handling; newly expanded results were checked through API/data, without claiming a fresh visual check of every reservoir.

Software tests do not supply independent chlorophyll or cyanobacteria reference measurements. We therefore report no Karnataka MAE, RMSE, R², sensitivity or toxicity-detection accuracy.

## VI. UNFINISHED WORK AND LIMITATIONS

A separate historical FAI acquisition workflow has 10,417 status records, including 5,220 marked valid at inspection: 1,802 in 2022, 1,973 in 2023 and 1,445 in 2024. These counts come from current persisted files, not an older progress summary. The work is incomplete and was not running at inspection. It was not restarted for this paper.

An offline Random Forest pipeline is prepared for a nominal ten-day future-FAI target, matched to observations seven to thirteen days later. It includes chronological partitions, target-window purging, a persistence baseline and explicit data gates. No future-FAI regression model is trained or deployed. This planned temporal prediction is different from CyFi estimation at an observed image date.

The main limitations are absent Karnataka field validation, uncertain radiometric/domain transfer, coarse or mixed pixels, cloud-related gaps and incomplete coverage. Positive or negative FAI, estimated chlorophyll and model-estimated cells represent different quantities. None establishes cyanotoxin concentration. A future evaluation needs independent local samples, matched acquisition times and a sampling plan that separates calibration from validation.

## VII. CONCLUSION

NEERWATCH implements a dated, provenance-bearing reservoir monitoring workflow with chlorophyll screening, observed FAI and a separate pretrained cyanobacteria regression path. The inspected application supports the fixed 46-reservoir inventory, with experimental CyFi estimates for 32 reservoirs. Its contribution is a working integration with explicit missing-data handling and reproducible software checks. Local biological accuracy and future forecasting remain unestablished and are not claimed.

## REFERENCES

[1] A. A. Gilerson et al., “Algorithms for remote estimation of chlorophyll-a in coastal and inland waters using red and near infrared bands,” Optics Express, vol. 18, no. 22, pp. 24109–24125, 2010, doi: 10.1364/OE.18.024109.

[2] C. Hu, “A novel ocean color index to detect floating algae in the global oceans,” Remote Sensing of Environment, vol. 113, no. 10, pp. 2118–2129, 2009, doi: 10.1016/j.rse.2009.05.012.

[3] DrivenData, “CyFi: Cyanobacteria Finder,” source code and pretrained model, MIT license. https://github.com/drivendataorg/cyfi. Inspected source commit: b89ad178e26e3a929f33b977ccff2cb9e0bceaba.

[4] G. Ke et al., “LightGBM: A Highly Efficient Gradient Boosting Decision Tree,” Advances in Neural Information Processing Systems, vol. 30, 2017.

[5] U.S. Environmental Protection Agency, “World Health Organization (WHO) 1999 Guideline Values for Cyanobacteria in Freshwater,” historical summary. https://www.epa.gov/habs/world-health-organization-who-1999-guideline-values-cyanobacteria-freshwater. Accessed 23 Oct. 2026.

[6] World Health Organization, Guidelines on Recreational Water Quality, vol. 1: Coastal and Fresh Waters, 2021. https://www.who.int/publications/i/item/9789240031302.

[7] NEERWATCH project repository and inspected implementation snapshot. https://github.com/shriya345/neerwatch. Data and software results reported in this paper refer to 23 Oct. 2026; they are not independent field validation.
