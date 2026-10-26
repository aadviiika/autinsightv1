# Model artifacts

`primary.joblib` is the trained XGBoost pipeline, preprocessing bundle, and TreeSHAP explainer produced by `python scripts/train_models.py`. `artifact_manifest.json` records the UCI source SHA-256, artifact SHA-256, target semantics, split size, seed, feature list, XGBoost parameters, thresholds, and versions. Rebuild with the same dataset checksum and code revision to reproduce the artifact. Load joblib only from a trusted project build.
