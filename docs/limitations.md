# Limitations

## UCI child dataset

- 292 source rows; 2 exact duplicates were removed before holdout splitting, leaving n=290.
- The label has perfect deterministic circularity: `result = sum(A1_Score…A10_Score)`, and `class=YES` exactly when `result >= 7`. Machine-learning metrics therefore measure reproduction of a questionnaire score threshold, not independent ASD identification.
- Source uses a small screening dataset and provides no independent clinical gold standard; population representativeness is unknown.
- Subgroup test counts are small, often fewer than 10 in ethnicity groups.

## Indian AIIMS validation cohort

- 225 children aged 1–14 were enrolled at a North Indian tertiary referral hospital after suspicion criteria; selection/spectrum bias limits population transportability.
- Publicly released 2019 S2 data are deidentified but include an ID field; it is excluded and raw data are not committed.
- The target is the study's DSM-5 expert consensus diagnosis, but the cohort and tool administration are not a prospective general-population screening sample.
- A single 75/25 split gives only 56 analyzed test cases. Metrics are exploratory; confidence intervals and repeated/nested validation are needed.
- The 2024 paper's AMI dataset is not assumed identical to the 2019 supplementary workbook.

## System-wide

- The system OpenMP runtime is not installed; the model was trained and the API verified using a checksum-verified local runtime. Mac users need `brew install libomp`; Linux deployments need a compatible OpenMP runtime.
- The API's P0–P3 thresholds are not calibrated or clinically justified.
- Counterfactuals, explanation fidelity/stability evaluation, video analysis, external clinical validation, clinical deployment, authentication and complete privacy governance are not implemented.
