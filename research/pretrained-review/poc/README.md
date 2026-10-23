# Isolated CyFi compatibility proof of concept

No application imports or writes. No writes to `data/fai-history`, its catalogue/checkpoints or the reservoir registry. No retraining. Source clones, environment, downloads and outputs are kept under this research directory. The historical acquisition process is left running.

## Reproduce

Run from the NEERWATCH repository root:

```sh
DYLD_LIBRARY_PATH="$PWD/research/pretrained-review/omp" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 research/pretrained-review/venv/bin/python research/pretrained-review/poc/run.py
DYLD_LIBRARY_PATH="$PWD/research/pretrained-review/omp" research/pretrained-review/venv/bin/python research/pretrained-review/poc/spatial_qc.py
.venv/bin/python research/pretrained-review/poc/check_feature_ranges.py
```

The isolated environment installs the cloned CyFi package without changing the application environment. Dependency versions are recorded in `output/pretrained-model-review/poc-environment.txt`. macOS ARM LightGBM required a local `libomp.dylib`, extracted from the conda-forge llvm-openmp package into the separate `omp` directory; its location is supplied only to these processes.

Inputs are the existing registry point coordinates and the newest entries in the **operational** Sentinel-2 history for KRS, Bhadra and Tungabhadra, not the actively written historical acquisition dataset. These are fixed-scene compatibility probes, not a demonstration of CyFi's full default automatic 30-day candidate search. Actual scene JSONs and all 15 required native-band crops are cached locally and hashed in `results.json`.

Upstream `FeaturesConfig`, box construction, per-scene spectral feature extraction and land-cover lookup are reused. Five original pretrained LightGBM boosters are loaded from the ZIP and averaged in log space; output follows upstream rounding of exp(log density)-1. A single candidate per point avoids candidate/batch-dependent winsorization changes. No synthetic band, filled label or guessed land-cover class is permitted.

The exact ancillary raster is downloaded from:
https://drivendata-public-assets.s3.amazonaws.com/land_cover_map.tar.gz

The required extracted file is `C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc` in this directory. If absent, the runner records a blocker and produces no density. If spectral QC fails, it also produces no density. No fallback imputes any required feature.

`spatial-qc.json` overlays genuine SCL water pixels against the existing polygons for attribution diagnostics. It does not silently alter the upstream mask. `feature-range-check.json` checks observed features against the ranges stored in each booster. Neither diagnostic establishes local biological accuracy.

Even a completed inference remains **experimental upstream inference only**, due to unresolved radiometric transfer and absent Karnataka field validation. It is not a future FAI forecast, toxin concentration, health advisory, or production-approved reservoir value.
