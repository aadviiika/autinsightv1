# Methodology

## Research question and source-label validity

The UCI analysis asks how classifiers reproduce the recorded screening class. A deterministic audit found `result == sum(A1_Score…A10_Score)` for every row, and `class == YES` exactly when `result >= 7`. This confirms that UCI's class is a questionnaire-derived rule. High ML performance on these features is not evidence of clinical diagnostic validity. A demographics-only model is included as a sensitivity analysis without the ten questionnaire items.

The separate Indian analysis asks whether questionnaire/context items predict the study's DSM-5 expert consensus diagnosis in the 2019 AIIMS modified INDT-ASD validation cohort. The PLOS article reports an independently adjudicated expert diagnosis by a pediatric neurologist, clinical psychologist and child psychiatrist. Participants were children suspected of ASD at a tertiary referral hospital; the estimates do not establish population screening performance. The raw supplement includes one 180-month age despite the article's 1–14-year stated range; this record is flagged and excluded from model training, leaving 224 records. The 2024 preprint's AMI data are not presumed identical to the S2 workbook.

## Audit and preprocessing

UCI acquisition records source, date, license and SHA-256. Its exact duplicate rows are removed before split. The `result`, constant `age_desc`, and identifiers are excluded. String quotes/whitespace/sentinels are normalized. Train-only median/mode imputers, one-hot encoders and numeric scaling are fit in scikit-learn pipelines.

For the Indian file, the target maps source code 1 to ASD and 2 to non-ASD, matching reported cohort counts 128/97. `Patient ID`, diagnostic summaries, old/new tool result fields, severity scores, CARS and DP3 measures are excluded to prevent target/outcome proxy leakage. The 28 instrument item codes are categorical; age in months is numeric; gender, SES and residence are categorical. Features, transformations and target counts are captured in the audit report.

## Experimental design and current results

Both datasets use a single stratified 75/25 holdout and seed 17, with preprocessing fit only on the training set. UCI contains 290 deduplicated records (217 train, 73 test); Indian has 224 analyzed records (168 train, 56 test) after excluding one source age above the stated 14-year study range. Models include Logistic Regression, Random Forest and the primary XGBoost model on UCI. XGBoost is trained with parameters in `models/artifact_manifest.json`; the local macOS host required an OpenMP runtime. The separate Indian cohort uses Logistic Regression and Random Forest only.

Metrics: accuracy, balanced accuracy, F1, ROC AUC, Brier score. UCI also reports a direct score-rule baseline, demographics-only sensitivity analysis, P0/P1 coverage/selective error under uncalibrated bins for Logistic Regression, Random Forest, and XGBoost, and gender/ethnicity subgroup counts with Wilson intervals for sensitivity. Indian fairness reporting is limited to source gender codes. Very small groups remain descriptive only. No UCI/Indian metric comparison is scientifically meaningful.

## Reliability and calibration

The API bins maximum class probability into P0 (≥.90), P1 (≥.80), P2 (≥.70), P3 (<.70), deferring P2/P3. These cutoffs are provisional engineering behavior, not trained or clinically justified. Experiment files report exploratory P0/P1 coverage and selective risk for all three UCI models, but no calibration curve or threshold-selection process exists. Future confirmatory work should prespecify a decision cost, use repeated/nested validation, estimate calibration on training-only cross-validation, and report uncertainty intervals, calibration plots, Brier score, coverage, and selective risk. Entropy and Jensen–Shannon divergence are not implemented.

## Explainability and counterfactuals

The experiment generated TreeSHAP for the comparative UCI Random Forest, including global mean absolute contributions and one held-out local example. Base value plus contributions reconstructed that example's predicted positive-class probability with absolute error 1.89e-15. This verifies SHAP additivity for one model/record only. The leading features are the questionnaire scores, consistent with the known circular label. The saved XGBoost artifact includes TreeSHAP and API local contributions, but XGBoost additivity was not independently tested. Explanation stability, perturbation fidelity, plausibility and user comprehension remain unevaluated. The API returns an empty list when no prediction artifact/explainer exists. Counterfactual generation is deferred until feasible mutable-feature constraints and domain review are available. No explanation is causal or clinical evidence.

## Population and external validity

UCI data has a circular screening target and uncertain sampling representativeness. Indian data is a small tertiary referral cohort of suspected cases. Neither analysis constitutes prospective community screening or supports deployment. Subgroup outputs are descriptive, with counts and uncertainty; no fairness guarantee is claimed.
