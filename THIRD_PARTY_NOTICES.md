# Reuse and scientific audit

WaterQual (https://github.com/iliasmachairas/WaterQual), inspected commit a9882bf: pure NumPy NDCI implementation copied into vendor/waterqual with GPL-2.0-or-later license. Its OC3 example coefficients and placeholder Gilerson coefficients were rejected for concentration retrieval. QGIS interface not reused.

FCMm (https://github.com/bishun945/FCMm), inspected commit bdd7ca0: R/Chla_estimation.R BR_Gil10 provides the published Gilerson power equation used as a numerical reference: (35.75 × R709/R665 − 19.3)^1.124. MIT, copyright Shun Bi (2020). No R source distributed here; independently expressed NumPy equation checked against the reference expression on actual KRS pixels. Original paper: https://doi.org/10.1364/OE.18.024109.

ACOLITE, commit ce6bd34, GPL-3.0: inspected aquatic atmospheric correction and L2W algorithms. Not installed or claimed to have been run. Requires additional native dependencies and input products. gee_acolite commit 95d86e8 GPL-3.0 requires authenticated Earth Engine; not executed.

Regional-HAB-Algorithms commit 0eaee66: inspected R workflow; no clear license found, no code copied. USEPA/modelling_hab_indices commit 05b8a51: legacy R modeling reference; not used for active retrieval. Original Nasios training reference remains in reference/; its competition labels are not used as Karnataka chlorophyll ground truth.

Official reservoir additions: Central Water Commission National Register of Large Dams 2019, https://www.cwc.gov.in/sites/default/files/nrld-2019.pdf. Each added entry includes PIC and physical PDF page. Coordinates are dam inventory points, not verified reservoir centroids/polygons. Existing water boundaries retain OpenStreetMap ODbL attribution.

EPA categories: https://nationallakesassessment.epa.gov/webreport/#trophic-state. Numeric ppb concentrations in freshwater correspond to µg/L; ≤2, >2–7, >7–30, >30. These describe trophic status, not toxicity.
