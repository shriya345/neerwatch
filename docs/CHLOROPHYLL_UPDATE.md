# Expansion and interface simplification — 22 October 2026

The active dashboard now contains 17 Karnataka reservoirs. Added Shanti Sagara, Markonahalli, Yagachi, Malaprabha (Renuka Sagara) and Hidkal, each with two official satellite CHL_NN concentrations. Boundaries come from OSM water features, with source URLs retained. Hidkal's multipolygon was assembled from the complete source relation, including inner rings. Only candidates with two passing observations were registered; Kanva and Manchanabele did not pass the cached-data screen and were not added.

The monthly-analysis menu and section are removed. The report shows dated observations instead of monthly aggregates. The separate cyanobacteria-dominance status row is removed, including from CSV output. The historical WHO reference captions retain their applicability condition; no unconditional safety limits are asserted.

All concentrations are satellite-derived estimates. CLMS OLCI products serve the original four reservoirs and official OLCI CHL_NN products serve the other thirteen. The displayed Sentinel-2 true-colour images provide visual context and are not converted into chlorophyll concentrations with an invented calibration. Weather/image panels are omitted for new reservoirs when those observations are not available. Original packing, units, geolocation, source hashes and quality flags remain preserved.

The production build and 30 integrity tests passed. The registry/API and pixel checks include all newly added reservoirs. No synthetic measurements or forecast values are added.

## Earlier implementation details

# Observed chlorophyll review — 22 October 2026

## Current scope

The user replaced forecasting with observed concentration comparisons and required/not-required monitoring review. Forecast, model evaluation/readiness and spectral-index selector panels are absent. The dashboard includes all twelve reservoirs, both concentrations and dates, absolute/percentage change, WHO reference context, monthly summaries and matching reports.

## Genuine data

The original four reservoirs retain 247 recomputed provisional CLMS ten-day estimates. Original raster hashes were checked against acquisition sidecars with explicit user permission. CHLAMEAN is mg/m³, numerically equivalent to µg/L. No old application code, synthetic data or model outputs were reused.

The eight previously uncovered reservoirs now each have two screened official Sentinel-3 OLCI Water Full Resolution Level-2 CHL_NN observations, independently downloaded through Microsoft Planetary Computer's public catalogue/blob service. No Copernicus secret was found or used. Latest screened dates found:

| Reservoir | Latest date | Concentration (µg/L) |
|---|---|---:|
| Kabini | 2026-02-08 | 5.30 |
| Harangi | 2026-02-20 | 4.76 |
| Hemavathi | 2026-02-20 | 5.50 |
| Almatti | 2026-02-20 | 8.81 |
| Basava Sagara | 2026-02-20 | 5.11 |
| Linganamakki | 2026-02-23 | 2.48 |
| Varahi (Mani Reservoir) | 2026-02-08 | 1.72 |
| Vani Vilasa Sagara | 2026-02-23 | 5.81 |

These are the most recent passing estimates found in the queried public archive, not claims that no newer observations exist in other services. The public collection's newest returned scene was 2026-02-23. Rejected newer candidates and query metadata are recorded. The authenticated CDSE download endpoint returned 401 without a token; the 100 m CLMS product documents Europe/Africa coverage and was not substituted for Karnataka.

## Decoding and quality

Source NetCDF files are checked against the STAC asset MD5 before extraction. Native latitude/longitude arrays locate each pixel. NetCDF scale/offset and fill masking are applied first, then log10(mg/m³) CHL_NN values are converted using 10**value. Units are verified from the original variable, rather than assumed from a filename.

Interior polygons exclude 300 m from the shoreline. The INLAND_WATER bit is required. LAND is deliberately not rejected because official OLCI documentation states inland water has both flags. Cloud, ambiguous cloud, cloud margin, invalid/cosmetic/suspect, saturation, high solar zenith, unreliable glint, snow/ice, atmospheric correction/NN failure and additional conservative project flags are excluded. Bit masks are read from each file's WQSF metadata, not hard-coded numeric guesses. At least three native valid pixels and 10% interior coverage are project sampling screens, not WHO rules. All accepted scenes cover the entire mapped reservoir footprint; current code requires at least 95% footprint coverage.

Source links, checked hashes, packing metadata, flags and compact native-pixel extracts (including rejected pixels inside the polygon) are included. Full original NetCDF files remain under data/cache/sentinel3 and are excluded from the source ZIP because of size. These global satellite retrievals have no established Karnataka field accuracy. CLMS estimates for the first four remain provisional pending full provider-flag review. No synthetic observations, daily interpolation or field-dominance claims are introduced.

## Review rules

- A positive change between comparable source/method observations triggers the user-requested trend review. WHO does not define this percentage-change rule.
- At or above the historical WHO 10 or 50 µg/L recreational-water reference, review is required, including confirmation of cyanobacteria dominance where unknown. A decline does not cancel a concentration-level review.
- Below the lower reference with no increase: review not required for the observed comparison.
- Without a concentration/comparable history: cannot determine; absence is not treated as clearance.

The historical WHO 1999/2003 framework is explicitly dated and sourced as summarized by EPA. Its chlorophyll guidance is conditional on established cyanobacteria dominance. None of the satellite estimates establishes dominance, toxicity or current water safety. These are archived observation reviews, not current health assessments or Karnataka regulatory classifications.

KRS example: 11.7793 µg/L for September 1–10, 2026 to 7.0074 µg/L for September 11–20, 2026; -40.511% change. The review is not required for this falling, below-reference historical comparison.

## Verification

Production build succeeded. Thirty tests cover existing integrity checks plus real KRS dates/values, falling-above-reference decisions, absent-data handling and the eight reservoirs' original decoded pixel medians/quality flags. Browser/API checks confirm all twelve have concentrations and two dated comparable estimates. PDF exports now match the observation review and omit forecasts and model evaluation.

Official sources:

- https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-3-olci-wfr-l2-netcdf
- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S3OLCIL2.html
- https://earth.esa.int/eogateway/documents/20142/1564943/Sentinel-3-OLCI-Marine-User-Handbook.pdf (Table 9; inland water/LAND note)
- https://www.epa.gov/habs/world-health-organization-who-1999-guideline-values-cyanobacteria-freshwater
