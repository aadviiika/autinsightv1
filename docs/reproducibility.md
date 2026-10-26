# Reproducibility

## Environment

Python 3.11 (or 3.12), Node 22, npm. On macOS, install `libomp` (`brew install libomp`) before XGBoost training. Raw data is ignored by git; retain provenance manifests and checksums.

## Commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_data.py
python scripts/validate_data.py
python scripts/run_eda.py
python scripts/train_models.py
python scripts/download_indian_data.py
python scripts/validate_indian_data.py
python scripts/run_indian_eda.py
python scripts/train_indian_models.py
pytest -q
ruff check backend scripts
```

Frontend checks: `cd frontend && npm ci && npm run typecheck && npm run lint && npm run build`.

Training uses seed 17 and one stratified 75/25 split. Outputs are `experiments/reports/data_quality.json`, `indian_data_quality.json`, generated plots, `experiments/results/model_metrics.json`, and `indian_model_metrics.json`. XGBoost writes `models/primary.joblib` and `models/artifact_manifest.json`; this versioned artifact is included. On macOS, install `libomp` before training/loading; CI and Linux containers should provide a compatible OpenMP runtime. Reported Logistic Regression/Random Forest results remain exploratory single-split findings, particularly invalid as clinical claims for UCI due exact label circularity.
