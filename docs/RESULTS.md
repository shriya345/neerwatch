# Current results and limitations

## Completed CAML training

The actual Downloads file contains 23,570 genuine source records. The schema/units audit is in `CAML_DATA_AUDIT.md`; its cells/L abundance declaration conflicts with source categories. Classification uses provided severity, without deriving corrected density or labels.

A disclosed 342-record class-enriched satellite acquisition pilot yielded 135 valid, strictly historical Sentinel-2 matchups. The new geographic split is 70 training / 24 validation / 41 fixed test; all five categories appear in all partitions. No original competition split is assumed.

| Model | Accuracy | Macro F1 | Macro precision | Macro recall |
|---|---:|---:|---:|---:|
| Neural network | 26.83% | 0.2055 | 0.1562 | 0.3067 |
| Random Forest | 26.83% | 0.2662 | 0.2915 | 0.3133 |

**The models are weak and exploratory.** Scores do not establish operational usefulness, full-CAML population accuracy or Karnataka field validation. Research estimates are shown on the dashboard but are excluded from monitoring alerts. Maximum class probabilities remain uncalibrated.

The fixed test was retained when repairing a development-validation split that lacked one category. The initial run and fixed-test audit are preserved in `reports/caml_split_audit.json`. No split was chosen using model/test performance.

Artifacts include both trained models, the training-only scaler, input hashes, split manifest, individual genuine held-out predictions and confusion matrices. The dashboard displays actual metrics, per-class support, source-unit limitations, both reservoir estimates and model agreement.

## Working observation application

Twelve sourced reservoir polygons, 17 accepted Sentinel-2 observations, and 612 reservoir-day NASA POWER records remain available. Nearby coordinates can share weather grid cells. Twenty satellite query windows provide sparse historical coverage, not daily coverage. Monthly estimated severity distributions now use the trained pilot.

## Verification

- Automated tests verify actual source parsing, unit-discrepancy preservation, strictly historical satellite matchups, no target-feature leakage, geographic partition separation, training-only scaling, test metric recomputation and nonoperational dashboard inference.
- React production build, API inference/evaluation/download routes, browser results and the updated PDF report are checked. See `reports/verification.json` for the final check count and scope.

## Still unavailable / unresolved

- Corrected abundance units require authoritative clarification. No numeric density model or density estimate is produced.
- Only 135 source records have approved aligned features in this initial class-enriched experiment. Extend acquisition and evaluate genuinely new held-out groups before claiming broader performance.
- The model has US training origin and has not been field-validated in Karnataka.
- A site-box training summary and a reservoir polygon differ in spatial support. Coordinate uncertainty and conservative water masks can bias coverage and sampling.
- No validated seven-day forecast is available. The task is same-date classification using historical features.
- No chlorophyll concentration was added from this dataset: it has no chlorophyll column. CLMS still needs credentials and provider-quality review, or documented real chlorophyll observations must be supplied.
- Some actual weather responses contain unusually high rainfall. Original values are preserved, flagged and excluded from screened totals pending source review.
- No toxicity or drinking-water safety determination is made.
- Application remains local; no previous HAB repository/site was used or modified.

Source: https://www.drivendata.org/competitions/143/tick-tick-bloom/page/879/ and DOI https://doi.org/10.5067/SeaBASS/CAML/DATA001 .
