# Current implemented NEERWATCH architecture

```mermaid
flowchart TD
    R[Fixed inventory: 46 Karnataka reservoirs] --> S[Sentinel-2 satellite processing and quality checks]
    S --> C[Cached chlorophyll-a estimates]
    S --> F[Validated observed FAI snapshot]
    C --> A[FastAPI monitoring API]
    F --> A
    A --> UI[React dashboard: observations, search and monitoring]
    A --> P[Existing PDF and CSV reports]

    B[Separate reviewed CyFi band crops: five sampled reservoirs] --> Q[Original CyFi features and quality gates]
    L[Verified C3S land-cover lookups] --> Q
    Q --> M[Five original pretrained LightGBM regressors]
    M --> E[Experimental inference cache: three estimates]
    Q --> W[Two scenes withheld by cloud screening]
    E --> X[Separate FastAPI CyFi endpoints]
    W --> X
    X --> U[Experimental ML Estimates section]

    H[Ongoing historical Sentinel-2 acquisition] --> D[Historical FAI files and checkpoints]
    D -. future frozen input .-> G[Implemented RF eligibility and evaluation code; not trained]
```

The CyFi path has no connection to operational alerts or existing reports. Forty-one reservoirs have no reviewed CyFi inputs in the published snapshot and explicitly return unavailable. The RF code exists, but there is no trained future-FAI model or forecast in this architecture. The existing acquisition process was not restarted or modified.
