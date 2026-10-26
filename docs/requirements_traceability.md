# Requirements traceability and evidence

The Phase I Review II presentation named in the initial brief was not included in the workspace. This table maps the prompt's major requirement groups to concrete files and execution evidence. Status values: **Implemented**, **Partial**, **Blocked**, **Future**.

| Requirement area | Implementation/evidence | Status |
|---|---|---|
| Monorepo and separation of concerns | `frontend/`, `backend/`, `scripts/`, `experiments/`, `docs/` | Implemented |
| UCI acquisition, license and provenance | `scripts/download_data.py`, `data/README.md`, `data/raw/provenance.json` | Implemented and run |
| Indian data authorization/provenance | `scripts/download_indian_data.py`, `data/raw/indian_provenance.json`; Figshare confirms CC BY 4.0 and matching file checksum | Implemented and run |
| Actual schema/missingness/duplicates/target audit | `scripts/validate_data.py`, `scripts/validate_indian_data.py`, reports under `experiments/reports/` | Implemented and run |
| UCI target circularity | `data_quality.json`: result equals A1–A10 sum; class is threshold at 7; score cross-tab | Implemented and verified |
| Indian target semantics and compatibility | `indian_data_quality.json`, [docs/data_dictionary.md](data_dictionary.md); kept separate from UCI | Implemented and verified |
| Exploratory analysis | `scripts/run_eda.py`, `scripts/run_indian_eda.py`, PNG and JSON outputs | Implemented and run |
| Leakage-safe preprocessing | scikit-learn pipelines; train-only fit; UCI duplicate/proxy exclusions; Indian ID/summary/clinical-measure exclusions | Implemented for baseline experiments |
| Comparative ML models | `scripts/train_models.py`, `scripts/train_indian_models.py`; Logistic Regression and Random Forest | Implemented and run |
| XGBoost primary | XGBoost trained on UCI and saved to `models/primary.joblib`; artifact manifest and test metrics generated | Implemented and run |
| Statistical comparison | Metrics on single stratified holdouts only; no repeated/nested inference | Partial |
| Calibration/reliability | Brier and provisional P0–P3 coverage/selective error for UCI baselines | Partial; no calibration model/curve or validated thresholds |
| SHAP global/individual explanations | Comparative UCI RF output includes global and one local TreeSHAP example; additivity error 1.89e-15; XGBoost local SHAP returned by API; RF global/local SHAP and additivity check available | Partial; primary XGB additivity not independently checked |
| Explanation-quality metrics | SHAP local additivity reconstruction checked for one held-out example; no fidelity/stability/usability evaluation | Partial |
| Counterfactual explanation | No algorithm; feasibility constraints documented | Future |
| Subgroup fairness | UCI gender/ethnicity summaries and Wilson sensitivity intervals; Indian source gender codes | Partial; too small/descriptive for fairness claims |
| FastAPI health/readiness/metadata/prediction | `backend/app/main.py` | Implemented; prediction readiness verified with versioned model artifact |
| Research metrics endpoints | `/research/metrics`, `/research/indian-metrics` | Implemented; real generated outputs returned |
| Next.js caregiver workflow | `/` → `/screening` (questionnaire and structured observations) → `/results` (caregiver summary, model explanation, next steps) | Implemented; source typecheck and ESLint passed after revision |
| Research charts and detailed model pages | Research metrics remain in experiment JSON and API endpoints; methodology and model detail pages are omitted from caregiver UI | Research artifacts retained for academic review |
| Accessibility and responsive design | Labels, responsive CSS, status/error rendering | Partial; no dedicated accessibility audit or E2E test |
| Automated backend tests | `backend/tests/test_api.py`; 4 passed | Implemented and run |
| Frontend tests/E2E | TypeScript, ESLint, Next production build run; no Playwright suite | Partial |
| CI | `.github/workflows/ci.yml` | Implemented; hosted CI not run |
| Deployment | Docker, Compose, Vercel config and guides | Prepared; no remote deployment; model artifact is available |
| Security/privacy docs | `docs/threat_model.md`, caregiver-facing privacy copy and CORS configuration | Partial; no auth/rate limiting/formal privacy review |
| Future video extension | Not implemented; identified as future work in README | Future |
| Required documentation set | README plus architecture, methodology, model card, data dictionary, reproducibility, limitations, threat model, deployment, ADRs | Implemented; claims/statuses explicit |

## Exact empirical artifacts

- UCI data provenance: `data/raw/provenance.json` (ignored raw-data folder).
- Indian data provenance: `data/raw/indian_provenance.json` (ignored raw-data folder).
- UCI schema/circularity report: `experiments/reports/data_quality.json`.
- Indian schema report: `experiments/reports/indian_data_quality.json`.
- Model outputs: `experiments/results/model_metrics.json`, `indian_model_metrics.json`.
- EDA outputs: `experiments/reports/*eda_summary.json`, `experiments/figures/*.png`.
- Verification in this environment: Python API tests 4 passed; Ruff passed; TypeScript, ESLint, Next.js build passed; npm audit reported zero vulnerabilities.
