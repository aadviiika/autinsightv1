# Data dictionary and field roles

## UCI child screening source

The observed raw file has 292 rows and 21 columns (20 predictor/source fields plus the class target). The complete observed types, missingness, cardinality, and raw values are in `experiments/reports/data_quality.json`.

| Source fields | Meaning/role | Model use | Audit use | Processing/notes |
|---|---|---:|---:|---|
| `A1_Score`…`A10_Score` | Questionnaire response codes (binary 0/1 in this file) | Yes, research only | no | Their sum exactly equals `result`; they determine target rule. |
| `age` | Age in years | Yes | optional subgroup | Numeric; 4 missing values, median imputation in fit pipeline. |
| `gender` | Categorical source demographic | Yes | subgroup | Values `m`, `f`; no broader claims. |
| `ethnicity` | Categorical source demographic | Yes | subgroup | 43 missing; category tokens contain quotes/whitespace; normalized before training. |
| `jaundice` | Source yes/no history field | Yes | no | One-hot encoded. |
| `autism` | Source yes/no family-history field (UCI description) | Yes as `family_history` | no | Normalized alias. |
| `country_of_res` | Reported country | Yes as `country` | no | 52 categories; small cells. |
| `used_app_before` | Previous application use | Yes | no | One-hot encoded. |
| `relation` | Respondent relationship | Yes as `who_completed` | no | 43 missing; mode imputation. |
| `result` | Integer score 0–10 | **Excluded** | leakage audit | Exactly equals A1–A10 sum. |
| `age_desc` | Constant age-band label | Excluded | no | Constant in this file. |
| `class` | Source screening class `NO`/`YES` | Target only | outcome | `YES` exactly when `result >= 7`; not clinical diagnosis. |

The caregiver web flow presents ten readability-adapted AQ-10 Child-Version-informed items in the source order, with four agreement choices. It maps each response to the source 0/1 scoring direction: agree-keyed items 1, 5, 7 and 10; disagree-keyed items 2, 3, 4, 6, 8 and 9. The wording adaptation means this web flow is not a validated AQ-10 administration and must not be interpreted using a clinical cut-off. The UCI `class` threshold of 7 is only the source dataset target rule. The source child-form guide and scoring direction are documented by the [NHS-hosted AQ-10 Child Version](https://northdevoncoastalpcn.nhs.uk/media/hypg30xa/aq-10child-autism.pdf).

## Indian AIIMS modified INDT-ASD validation cohort

The publicly released S2 workbook contains 225 rows and 53 columns. Full observed field details are in `experiments/reports/indian_data_quality.json`. The `DSM 5 gold standard diagnosis` target has values 1 (128 children with ASD) and 2 (97 without ASD), consistent with the paper's cohort counts. Model training maps 1→positive, 2→negative.

The raw workbook contains 225 rows. One record reports age 180 months, above the article's stated 14-year maximum; it is flagged and excluded from the modeling sample (224 remain). The 28 question fields are `New 1a1`…`New 2d4` as supplied in the workbook; they are treated as categorical codes because the source instrument uses yes/no/unsure and the numeric encoding was not self-describing. `Age in months` is numeric. `Gender`, `SES Kuppuswamy`, and `Residence` are categorical. Excluded from prediction: `Patient ID`, old-tool labels, new-tool summary/final scores, section outcomes, onset/functioning summary items, severity, CARS fields, DP3 fields, and the DSM-5 target itself. The workbook is deidentified but patient IDs remain present in source; IDs are never used as predictors.

The Indian instrument has different questions and a DSM-5 expert diagnosis target, unlike the UCI questionnaire threshold target. These datasets are analyzed separately and their scores are not pooled or directly compared.
