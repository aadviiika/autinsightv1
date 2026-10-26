"""Create a factual schema, missingness, duplicate, and target audit report."""

from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [ROOT / "data/raw/uci_asd_children.csv", ROOT / "data/raw/Autism-Child-Data.arff"]


def load() -> pd.DataFrame:
    path = next((p for p in CANDIDATES if p.exists()), None)
    if path is None:
        raise SystemExit(
            "Dataset missing. Run python scripts/download_data.py; see data/README.md."
        )
    if path.suffix == ".arff":
        from scipy.io import arff

        raw, _ = arff.loadarff(path)
        frame = pd.DataFrame(raw).map(lambda x: x.decode() if isinstance(x, bytes) else x)
        return frame
    return pd.read_csv(path)


def main() -> None:
    frame = load()
    report = {
        "rows": len(frame),
        "columns": len(frame.columns),
        "fields": {},
        "duplicate_rows": int(frame.duplicated().sum()),
        "target_candidates": {},
        "target_leakage_notes": [
            "Exclude total score/result and target aliases from predictors.",
            "The questionnaire-derived target may be circular with A1-A10; this dataset cannot establish diagnostic validity.",
        ],
    }
    for column in frame:
        series = frame[column].replace(r"^\\s*$", pd.NA, regex=True)
        report["fields"][column] = {
            "dtype": str(frame[column].dtype),
            "missing": int(series.isna().sum()),
            "unique_count": int(series.nunique(dropna=True)),
            "values": [str(v) for v in series.dropna().unique()[:40]],
        }
    for column in frame:
        if column.lower().replace(" ", "") in {"class/asd", "class_asd", "class", "asd"}:
            report["target_candidates"][column] = (
                frame[column].value_counts(dropna=False).astype(str).to_dict()
            )
    question_columns = [f"A{i}_Score" for i in range(1, 11)]
    if all(column in frame for column in question_columns) and "result" in frame:
        response_sum = frame[question_columns].apply(pd.to_numeric, errors="coerce").sum(axis=1)
        numeric_result = pd.to_numeric(frame["result"], errors="coerce")
        report["circularity_audit"] = {
            "result_equals_sum_of_A1_to_A10": bool((response_sum == numeric_result).all()),
            "class_is_threshold_of_result_at_7": bool(
                (frame["class"].astype(str).str.upper().eq("YES") == numeric_result.ge(7)).all()
            )
            if "class" in frame
            else None,
            "result_class_cross_tab": pd.crosstab(
                frame["result"], frame.get("class", pd.Series(index=frame.index, dtype=str))
            ).to_dict(),
        }
    out = ROOT / "experiments/reports/data_quality.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(f"Wrote {out}; {len(frame)} rows, {len(frame.columns)} columns")


if __name__ == "__main__":
    main()
