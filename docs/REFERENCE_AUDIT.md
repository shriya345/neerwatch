# Reference repository audit and attribution

Inspected repository: https://github.com/IoannisNasios/HarmfulAlgalBloomDetection
Pinned commit: `1d127630b0678589c5bd2e257b7c289f686956cb`
Inspected 22 October 2026.

## Existing components

| Notebook | Inspected methodology | Adaptation in the new project |
|---|---|---|
| `download_satellite_PlanetaryComputer.ipynb` | Historical STAC location/date search; buffered sample sites; satellite crops; band mean/median features; 10-day backward queries | `pipeline/satellite.py`, `pipeline/prepare.py` implement resumable, historical Sentinel-2 acquisition with explicit dates and quality checks |
| `download_satellite_EarthEngine.ipynb` | Earth Engine multispectral exports; AOI clipping; notebook filesystem conventions; per-crop display transformations | Public STAC replaces the credential-heavy notebook workflow; native reflectance scale/offset is retained for physical index calculations |
| `download_clima_noaahrrr.ipynb` | NOAA HRRR climate acquisition; several weather variables and aggregation windows | NASA POWER replaces US-specific HRRR for Karnataka weather context; weather is not silently substituted for lake measurements |
| `download_DEM_PlanetaryComputer.ipynb` | DEM acquisition and elevation/statistical features | Inspected; optional DEM features are omitted from the compact first implementation |
| `make_datasets.ipynb` | UID joins, image band means/medians/standard deviations, date/location features, climate statistics | UID-validated feature tables, valid-water band mean/median/std, NDCI/NDWI/FAI, explicit spatial and temporal validation |
| `lgbmNN_ee_gkf_S_v42g.ipynb` | GroupKFold geographic clustering, LightGBM, neural networks, target encodings, multiple image/time branches, tuning and ensemble experiments | A compact five-class PyTorch MLP and Random Forest share one geographic train/validation/test split; no ensemble or copied competition scores |

The notebooks rely on notebook execution state, local input folders, substantial downloaded feature data and heavyweight training dependencies. They are a research reference rather than a ready React/API application. Running all notebook cells blindly would not produce a working Karnataka website.

The new code is an independent implementation of the useful methodology. It does not copy trained predictions, target encodings, global imputations, competition leaderboard scores or notebook output tables into the dashboard. In particular, missing features are rejected rather than filled from the entire dataset, and all feature scaling is fitted using the training partition only.

## Licence and preservation

No `LICENSE` file or explicit reuse licence was present in the tracked tree at the inspected commit. The original notebooks/readme/banner are retained unchanged in `reference/` for local inspection and attribution. This is not an assertion that the source is openly licensed for redistribution; confirm terms with the author before public redistribution of those notebooks. They are not served by the website or included in its JavaScript bundle.

## Citation requested by the original author

Nasios, Ioannis (2025). “AI-driven multi-source data fusion for algal bloom severity classification in small inland water bodies: Leveraging Sentinel-2, DEM, and NOAA climate data.” Remote Sensing Applications: Society and Environment, 40, 101800.

Preprint: https://arxiv.org/abs/2505.03808

The upstream README reports a competition placement and leaderboard score. Those are the upstream author's results, not results of this new project, and are not used as this project's evaluation.
