# Model card

## Status

A versioned primary XGBoost artifact is present at `models/primary.joblib`; its checksum and training metadata are in `models/artifact_manifest.json`. Artifact version: `autinsight-0.1.0-uci419-seed17`. `/ready` and a genuine prediction were verified with a compatible OpenMP runtime.

## Intended use and limits

Caregiver-facing demonstration of how a research model reproduces a questionnaire-derived dataset label, and an aid for organizing observations before a professional conversation. Not intended for diagnosis, triage, treatment selection, reassurance, clinical use, or general-population screening. The adapted caregiver wording and flow are not a validated administration of AQ-10.

## Data and target

UCI: 292 rows, 2 exact duplicates removed; target `class` is exactly a threshold rule from the sum of A1–A10, not a clinical diagnosis. Indian: PLOS 2019 S2 deidentified cohort, 225 raw records; one 180-month age exceeds the publication stated range and is excluded, leaving 224 analyzed records (127 ASD, 97 non-ASD). Target is DSM-5 expert consensus diagnosis. These datasets have different instruments and labels; no pooling.

## Evaluation

Exploratory single stratified 75/25 holdouts, seed 17. Models are Logistic Regression, Random Forest, and primary UCI XGBoost. Actual metrics are in `experiments/results/`. No external validation, repeat validation, or calibrated operating threshold is available. UCI performance specifically reflects a questionnaire-derived outcome. Indian performance is from a tertiary referral/suspected-case sample.

## Explanation/reliability/safety

The XGBoost artifact includes a TreeSHAP explainer and local API output. Comparative Random Forest global/local TreeSHAP has a 1.89e-15 additivity reconstruction error; XGBoost additivity was not independently verified. Provisional P0–P3 bins are uncalibrated. Counterfactuals are not implemented. Do not use outputs to make clinical decisions. Require clinical, ethical, privacy, security and institutional oversight before any applied research.
