# Data acquisition and provenance

## Primary: UCI child questionnaire dataset

UCI dataset 419, *Autistic Spectrum Disorder Screening Data for Children*, DOI 10.24432/C5659W, CC BY 4.0. Run `python scripts/download_data.py`; the official UCI client fetches the artifact and writes the CSV plus date/checksum manifest in ignored `data/raw/`. The acquired file has 292 rows and 21 columns, including the `class` target. Source documentation describes the current UCI record as 292 instances and 20 features.

Observed audit findings: age missing=4; ethnicity missing=43; respondent relation missing=43; duplicate rows=2; class NO=151 and YES=141. `result` is the sum of A1–A10 and class is exactly `YES` when `result >= 7`. The score and constant `age_desc` are excluded from predictors; exact duplicate rows are removed before train/test split. This target is a questionnaire screening rule, not a clinical diagnosis.

## Secondary: AIIMS modified INDT-ASD S2 cohort

The 2019 PLOS ONE study's S2 deidentified workbook is publicly available through Figshare article 7840055, file 14600243, DOI 10.1371/journal.pone.0213242.s002, CC BY 4.0. `python scripts/download_indian_data.py` confirms the DOI, license, file identity and MD5 checksum before saving `aiims_modified_indt_asd_s2.xlsx`. Provenance is in `indian_provenance.json`. The source workbook contains 225 children and 53 columns; the gold-standard target is 128 ASD and 97 non-ASD. `python scripts/validate_indian_data.py` audits exact fields.

This is a North Indian tertiary referral cohort from the 2019 validation study, not automatically the same dataset as the separate 2024 preprint's AIIMS Modified database. The workbook's 28 question items and DSM-5 expert target are analyzed separately from UCI; the two datasets are not pooled or directly compared because questionnaire and label definitions differ.

Raw files are ignored by git. Acquire them from the authoritative links above. Do not redistribute raw data outside the applicable CC BY terms and attribution.
