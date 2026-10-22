# Architecture

```mermaid
flowchart TD
    DD[Real SeaBASS CAML source categories and metadata] --> Align[Historical coordinate/date alignment]
    STAC[Public Sentinel-2 L2A STAC] --> QC[Polygon + SCL + shoreline + reflectance QC]
    QC --> Features[Valid-water statistics and spectral indices]
    Features --> Align
    Align --> Split[Geographic train / validation / test split]
    Split --> Scale[Training-only scaler]
    Scale --> MLP[Five-class PyTorch MLP]
    Scale --> RF[Random Forest baseline]
    MLP --> Eval[Genuine held-out metrics and confusion matrices]
    RF --> Eval
    Eval --> Artifacts[Models + metadata + split manifest]
    QC --> Archive[Timestamped reservoir observation archive]
    OSM[Sourced OSM reservoir polygons] --> QC
    NASA[NASA POWER weather] --> Archive
    CLMS[Copernicus CLMS / documented chlorophyll] --> Review[Provider quality and provenance review]
    Review --> Archive
    Archive --> API[FastAPI]
    Artifacts --> API
    API --> Monitor[Explainable monitoring rules]
    Monitor --> React[React Karnataka dashboard]
    API --> PDF[Downloadable PDF reports]
```

The frontend calls only the same-origin `/api` endpoints. Remote collection and credentialed services run in Python scripts, never in React. The API uses saved real observations for fast and reproducible display. Public, read-only endpoints expose reservoir data, mapped geometry, model status, report downloads and accepted satellite images. There is no unauthenticated mutation/credential endpoint.

The built frontend can be served by FastAPI from `frontend/dist`. Development Vite proxies to the same API. JSON writes are atomic in the collection path. Missing observations produce explicit unavailable states rather than client-side demonstrations or generated values.
