# Short presentation/demo guide

1. Start the API using the README command and open http://127.0.0.1:8010/.
2. Introduce the Karnataka reservoir monitoring objective. Select Bhadra, KRS, Tungabhadra and Supa from the map/list.
3. Show actual observation dates, valid-water coverage, NASA POWER weather and the dated Sentinel-2 true-colour image. Explain that the satellite view and gridded weather are real retrieved observations, while neither establishes toxins.
4. Switch the history selector between NDCI, NDWI and FAI. Explain why missing periods are not filled and why spectral indices are not chlorophyll concentrations.
5. Show all five density ranges with the direct DrivenData caption. Show the two historical WHO guidance values, their direct captions and the cyanobacteria-dominance condition.
6. Show monthly coverage, weather summaries and missing windows. Download the selected reservoir report.
7. Open Evaluation and readiness. Show the actual 135-record acquisition pilot and the new 70/24/41 geographic partitions. Neural-network accuracy is 26.83% with macro F1 0.2055; Random Forest accuracy is 26.83% with macro F1 0.2662. Explain that this is weak exploratory performance and not Karnataka validation. Expand per-class results and show the confusion matrices.
8. Explain the pipeline: genuine field labels → historical imagery → quality control → geographic split → optimized MLP vs Random Forest → actual held-out evaluation. The training data's origin is the United States, not Karnataka.
9. State the remaining work: authoritative abundance-unit clarification, larger genuine matchups and improved held-out performance, Copernicus access/product-quality review, Karnataka field validation, and only then a validated future-target forecast.

Suggested project claim now: **A working Karnataka reservoir observation application with a genuinely trained, weak-performing CAML severity pilot and transparent source-unit limitations.**

Do not claim: a completed trained/validated Karnataka seven-day HAB forecaster, toxicity detector, drinking-water safety system, or invented performance improvement.
