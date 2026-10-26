.PHONY: data validate eda train indian-data indian-validate indian-eda indian-train test api frontend

data:
	python scripts/download_data.py
validate:
	python scripts/validate_data.py
eda:
	python scripts/run_eda.py
train:
	python scripts/train_models.py
indian-data:
	python scripts/download_indian_data.py
indian-validate:
	python scripts/validate_indian_data.py
indian-eda:
	python scripts/run_indian_eda.py
indian-train:
	python scripts/train_indian_models.py
test:
	pytest -q
api:
	uvicorn backend.app.main:app --reload
frontend:
	cd frontend && npm run dev
