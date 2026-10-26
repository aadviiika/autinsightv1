"""Train leakage-conscious baselines on a stratified holdout; no results without source data."""

from pathlib import Path
from datetime import date
import hashlib
import json
import re
import math
import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    roc_auc_score,
    brier_score_loss,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from validate_data import load

ROOT = Path(__file__).resolve().parents[1]


def wilson_interval(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    z = 1.96
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total))
        / denominator
    )
    return [max(0.0, center - margin), min(1.0, center + margin)]


def normalize(name: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    aliases = {
        "austim": "family_history",
        "autism": "family_history",
        "contry_of_res": "country",
        "country_of_res": "country",
        "who_completed_the_test": "who_completed",
        "relation": "who_completed",
        "used_app_before": "used_app_before",
        "class_asd": "class_asd",
        "age_desc": "age_desc",
    }
    return aliases.get(key, key)


def main() -> None:
    frame = load().copy()
    duplicate_rows = int(frame.duplicated().sum())
    frame = frame.drop_duplicates().reset_index(drop=True)
    for column in frame.select_dtypes(include="object"):
        frame[column] = frame[column].map(
            lambda value: value.strip().strip("'\"").strip() if isinstance(value, str) else value
        )
        frame[column] = frame[column].replace(
            {"?": np.nan, "": np.nan, "NA": np.nan, "unknown": np.nan}
        )
    frame.columns = [normalize(str(c)) for c in frame.columns]
    target = next((c for c in ("class_asd", "class", "asd") if c in frame), None)
    if not target:
        raise SystemExit("No Class/ASD target found. Inspect the source schema before training.")
    y_raw = frame.pop(target).astype(str).str.strip().str.lower()
    y = y_raw.map({"yes": 1, "1": 1, "true": 1, "no": 0, "0": 0, "false": 0})
    if y.isna().any():
        raise SystemExit(f"Unexpected target labels: {sorted(y_raw[y.isna()].unique())}")
    # Remove explicit score/outcome proxies, IDs, and constant fields.
    drop = [
        c
        for c in frame
        if c in {"result", "screening_result", "id", "age_desc"}
        or frame[c].nunique(dropna=True) <= 1
    ]
    X = frame.drop(columns=drop)
    numeric = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    prep = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
                ),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )
    estimators = {
        "logistic_regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=17
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=400, class_weight="balanced", min_samples_leaf=2, random_state=17
        ),
    }
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=17
    )
    results = {
        "protocol": "single stratified 75/25 holdout; random_state=17; no external validation",
        "n_total": len(y),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "exact_duplicates_removed": duplicate_rows,
        "excluded_columns": drop,
        "models": {},
    }
    best = None
    if estimators.get("xgboost") is None:
        try:
            from xgboost import XGBClassifier

            estimators["xgboost"] = XGBClassifier(
                n_estimators=250,
                max_depth=3,
                learning_rate=0.03,
                subsample=0.85,
                colsample_bytree=0.85,
                eval_metric="logloss",
                random_state=17,
                n_jobs=1,
            )
        except Exception:
            results["models"]["xgboost"] = {
                "status": "blocked",
                "reason": "XGBoost runtime unavailable; macOS requires OpenMP (brew install libomp).",
            }
    for name, estimator in estimators.items():
        pipe = Pipeline([("preprocess", prep), ("model", estimator)])
        pipe.fit(X_train, y_train)
        prob = pipe.predict_proba(X_test)[:, 1]
        pred = (prob >= 0.5).astype(int)
        scores = {
            "accuracy": accuracy_score(y_test, pred),
            "balanced_accuracy": balanced_accuracy_score(y_test, pred),
            "f1": f1_score(y_test, pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, prob),
            "brier": brier_score_loss(y_test, prob),
        }
        tiers = np.where(
            np.maximum(prob, 1 - prob) >= 0.90,
            "P0",
            np.where(
                np.maximum(prob, 1 - prob) >= 0.80,
                "P1",
                np.where(np.maximum(prob, 1 - prob) >= 0.70, "P2", "P3"),
            ),
        )
        accepted = np.isin(tiers, ["P0", "P1"])
        scores["reliability_placeholder"] = {
            "coverage_p0_p1": float(accepted.mean()),
            "selective_risk_p0_p1": float((pred[accepted] != y_test.to_numpy()[accepted]).mean())
            if accepted.any()
            else None,
            "tier_counts": {tier: int((tiers == tier).sum()) for tier in ["P0", "P1", "P2", "P3"]},
            "note": "Uncalibrated confidence bins; exploratory only.",
        }
        subgroup_results = {}
        for protected in ["gender", "ethnicity"]:
            if protected not in X_test:
                continue
            subgroup_results[protected] = {}
            groups = X_test[protected].fillna("Missing").astype(str)
            for group in sorted(groups.unique()):
                mask = groups.to_numpy() == group
                actual = y_test.to_numpy()[mask]
                predicted = pred[mask]
                positives = int(actual.sum())
                subgroup_results[protected][group] = {
                    "n": int(mask.sum()),
                    "interpretation_adequate_n_10": bool(mask.sum() >= 10),
                    "accuracy": float((predicted == actual).mean()),
                    "sensitivity": float(((predicted == 1) & (actual == 1)).sum() / positives)
                    if positives
                    else None,
                    "sensitivity_wilson_95": wilson_interval(
                        int(((predicted == 1) & (actual == 1)).sum()), positives
                    ),
                }
        scores["subgroup_metrics"] = subgroup_results
        results["models"][name] = scores
        if name == "random_forest":
            import shap

            transformed_test = pipe.named_steps["preprocess"].transform(X_test)
            if hasattr(transformed_test, "toarray"):
                transformed_test = transformed_test.toarray()
            transformed_test = np.asarray(transformed_test, dtype=float)
            feature_names = list(pipe.named_steps["preprocess"].get_feature_names_out())
            rf_explainer = shap.TreeExplainer(pipe.named_steps["model"])
            shap_values = np.asarray(rf_explainer.shap_values(transformed_test))
            positive_values = shap_values[:, :, 1] if shap_values.ndim == 3 else shap_values
            global_values = np.mean(np.abs(positive_values), axis=0)
            global_ranked = sorted(
                [
                    {"feature": name, "mean_abs_shap": float(value)}
                    for name, value in zip(feature_names, global_values)
                ],
                key=lambda item: item["mean_abs_shap"],
                reverse=True,
            )[:10]
            local = positive_values[0]
            local_ranked = sorted(
                [
                    {"feature": name, "contribution": float(value)}
                    for name, value in zip(feature_names, local)
                ],
                key=lambda item: abs(item["contribution"]),
                reverse=True,
            )[:10]
            expected = np.asarray(rf_explainer.expected_value).reshape(-1)
            base_value = float(expected[-1])
            scores["shap_tree_explainer"] = {
                "scope": "comparative Random Forest baseline, not primary XGBoost",
                "global_top_10": global_ranked,
                "example_test_record_top_10": local_ranked,
                "example_test_record_index": 0,
                "additivity_error_vs_positive_probability": float(
                    abs(base_value + positive_values[0].sum() - prob[0])
                ),
                "warning": "SHAP explains this fitted model, not causality or diagnosis; single split, exploratory only.",
            }
            results["models"][name] = scores
        if name == "xgboost":
            # TreeSHAP explains the transformed features from this fitted pipeline.
            import shap

            explainer = shap.TreeExplainer(pipe.named_steps["model"])
            transformed_names = list(pipe.named_steps["preprocess"].get_feature_names_out())
            best = {
                "pipeline": pipe,
                "feature_names": list(X.columns),
                "version": "autinsight-0.1.0-uci419-seed17",
                "explainer": explainer,
                "explanation_feature_names": transformed_names,
                "thresholds": {"P0": 0.90, "P1": 0.80, "P2": 0.70},
            }
    question_columns = [f"a{i}_score" for i in range(1, 11) if f"a{i}_score" in X_test.columns]
    if len(question_columns) == 10:
        rule_prediction = (X_test[question_columns].sum(axis=1).to_numpy() >= 7).astype(int)
        results["deterministic_questionnaire_rule"] = {
            "rule": "sum(A1_Score..A10_Score) >= 7",
            "accuracy": accuracy_score(y_test, rule_prediction),
            "balanced_accuracy": balanced_accuracy_score(y_test, rule_prediction),
            "f1": f1_score(y_test, rule_prediction, zero_division=0),
            "interpretation": "Reconstructs the dataset's questionnaire-derived screening class; not diagnostic validation.",
        }
        demo_columns = [column for column in X.columns if column not in question_columns]
        demo_numeric = [column for column in demo_columns if column in numeric]
        demo_categorical = [column for column in demo_columns if column in categorical]
        demo_prep = ColumnTransformer(
            [
                (
                    "numeric",
                    Pipeline(
                        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
                    ),
                    demo_numeric,
                ),
                (
                    "categorical",
                    Pipeline(
                        [
                            ("impute", SimpleImputer(strategy="most_frequent")),
                            ("encode", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    demo_categorical,
                ),
            ]
        )
        demo_pipe = Pipeline(
            [
                ("preprocess", demo_prep),
                (
                    "model",
                    LogisticRegression(max_iter=2000, class_weight="balanced", random_state=17),
                ),
            ]
        )
        demo_pipe.fit(X_train[demo_columns], y_train)
        demo_probability = demo_pipe.predict_proba(X_test[demo_columns])[:, 1]
        demo_prediction = (demo_probability >= 0.5).astype(int)
        results["demographics_only_logistic_regression"] = {
            "accuracy": accuracy_score(y_test, demo_prediction),
            "balanced_accuracy": balanced_accuracy_score(y_test, demo_prediction),
            "f1": f1_score(y_test, demo_prediction, zero_division=0),
            "roc_auc": roc_auc_score(y_test, demo_probability),
            "brier": brier_score_loss(y_test, demo_probability),
            "features": demo_columns,
            "interpretation": "Sensitivity analysis without A1-A10; target is still questionnaire-derived.",
        }

    outdir = ROOT / "experiments/results"
    outdir.mkdir(exist_ok=True, parents=True)
    (outdir / "model_metrics.json").write_text(json.dumps(results, indent=2) + "\n")
    if best is not None:
        modeldir = ROOT / "models"
        modeldir.mkdir(exist_ok=True)
        provenance_path = ROOT / "data/raw/provenance.json"
        provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
        best["metadata"] = {
            "artifact_version": "autinsight-0.1.0-uci419-seed17",
            "trained_date": date.today().isoformat(),
            "dataset_id": 419,
            "dataset_sha256": provenance.get("sha256"),
            "target": "class: YES=1, NO=0; label is exactly result >= 7 and result is the A1-A10 sum",
            "train_rows": len(y_train),
            "test_rows": len(y_test),
            "random_seed": 17,
            "model": "XGBoostClassifier",
            "xgboost_parameters": {
                "n_estimators": 250,
                "max_depth": 3,
                "learning_rate": 0.03,
                "subsample": 0.85,
                "colsample_bytree": 0.85,
                "eval_metric": "logloss",
                "random_state": 17,
            },
            "software": {
                "scikit_learn": __import__("sklearn").__version__,
                "xgboost": __import__("xgboost").__version__,
            },
        }
        artifact = modeldir / "primary.joblib"
        joblib.dump(best, artifact)
        manifest = {
            **best["metadata"],
            "filename": artifact.name,
            "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "feature_names": list(X.columns),
            "thresholds": best["thresholds"],
        }
        (modeldir / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
