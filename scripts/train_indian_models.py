"""Independent Indian validation-cohort experiment; never pooled with UCI."""

from pathlib import Path
import json
import math
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
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
from validate_indian_data import load

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {
    "Patient ID",
    "Old tool ASD",
    "Old tool number of criteria",
    "Old tool final",
    "newtoolseverity",
    "Section A1",
    "Section A2",
    "New onset early development",
    "New impaired functioning",
    "New final tool ASD",
    "New final summary ASD",
    "CARS Raw",
    "CARS Severity",
    "DP3 Physical",
    "DP3 Adaptive",
    "DP3 Social",
    "DP3 Cognitive",
    "DP3 Communication",
    "DP3 DQ",
    "DP3 interpretation",
    "DSM 5 gold standard diagnosis",
}


def wilson(success: int, total: int) -> list[float] | None:
    if not total:
        return None
    z = 1.96
    p = success / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [max(0.0, center - margin), min(1.0, center + margin)]


def main() -> None:
    frame = load().copy()
    age_outliers = pd.to_numeric(frame["Age in months"], errors="coerce") > 168
    excluded_age_records = int(age_outliers.sum())
    frame = frame.loc[~age_outliers].copy()
    target_raw = frame.pop("DSM 5 gold standard diagnosis")
    # The study reports 128 ASD and 97 non-ASD; the single >14-year source outlier is excluded.
    y = target_raw.map({1: 1, 2: 0})
    if y.isna().any() or len(y) != 224 or int(y.sum()) != 127:
        raise SystemExit(
            "Unexpected target encoding or sample counts. Review the source publication."
        )
    features = frame.drop(columns=[column for column in EXCLUDED if column in frame])
    numeric = ["Age in months"] if "Age in months" in features else []
    categorical = [column for column in features if column not in numeric]
    numeric_pipeline = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    categorical_pipeline = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        [("numeric", numeric_pipeline, numeric), ("categorical", categorical_pipeline, categorical)]
    )
    X_train, X_test, y_train, y_test = train_test_split(
        features, y, test_size=0.25, stratify=y, random_state=17
    )
    models = {
        "logistic_regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=17
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=400, class_weight="balanced", min_samples_leaf=2, random_state=17
        ),
    }
    results = {
        "protocol": "single stratified 75/25 holdout; random_state=17; exploratory; no external validation",
        "n_total": len(y),
        "excluded_age_over_168_months": excluded_age_records,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "target_positive": int(y.sum()),
        "feature_count": len(features.columns),
        "features": list(features.columns),
        "excluded_columns": sorted(EXCLUDED & set(frame.columns)),
        "models": {},
        "population_limit": "Tertiary referral cohort of children already suspected of ASD; spectrum and selection bias limit generalization.",
    }
    for name, estimator in models.items():
        pipe = Pipeline([("preprocess", preprocessor), ("model", estimator)])
        pipe.fit(X_train, y_train)
        probability = pipe.predict_proba(X_test)[:, 1]
        prediction = (probability >= 0.5).astype(int)
        metrics = {
            "accuracy": accuracy_score(y_test, prediction),
            "balanced_accuracy": balanced_accuracy_score(y_test, prediction),
            "f1": f1_score(y_test, prediction, zero_division=0),
            "roc_auc": roc_auc_score(y_test, probability),
            "brier": brier_score_loss(y_test, probability),
        }
        subgroups = {}
        for group in sorted(X_test["Gender"].dropna().unique()):
            mask = X_test["Gender"].to_numpy() == group
            actual, predicted = y_test.to_numpy()[mask], prediction[mask]
            positive_count = int(actual.sum())
            true_positive = int(((actual == 1) & (predicted == 1)).sum())
            subgroups[str(int(group))] = {
                "n": int(mask.sum()),
                "sensitivity": true_positive / positive_count if positive_count else None,
                "sensitivity_wilson_95": wilson(true_positive, positive_count),
                "adequate_n_10": int(mask.sum()) >= 10,
            }
        metrics["gender_subgroups"] = subgroups
        results["models"][name] = metrics
    out = ROOT / "experiments/results/indian_model_metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, default=str) + "\n")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
