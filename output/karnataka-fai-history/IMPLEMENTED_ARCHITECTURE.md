# Implemented architecture — acquisition stage

```mermaid
flowchart TD
  R[Existing 46 reservoir polygons] --> Q[Sentinel-2 L2A catalogue queries]
  Q --> C[Cached pages and deduplicated acquisitions]
  C --> B[Retrieve SCL and B04/B08/B11]
  B --> M[Water, cloud, shadow and shoreline QC]
  M --> F[Calculate observed FAI]
  F --> S[Saved NPZ arrays and JSON provenance]
  S --> H[Historical CSV and 10-day candidate pairs]
  M --> X[Recorded rejection or download error]
  X --> C
  E[Existing chlorophyll pipeline] --> D[Existing NEERWATCH dashboard]
```

The observed-FAI history branch is running and incomplete. A trained regressor and FAI dashboard integration are not yet implemented and are intentionally absent from this diagram.
