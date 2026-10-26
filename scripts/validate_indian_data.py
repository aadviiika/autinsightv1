"""Audit the public PLOS S2 workbook without exposing it in version control."""

from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/aiims_modified_indt_asd_s2.xlsx"


def load() -> pd.DataFrame:
    if not SOURCE.exists():
        raise SystemExit("Run python scripts/download_indian_data.py first.")
    frame = pd.read_excel(SOURCE)
    frame.columns = frame.columns.astype(str).str.strip()
    return frame


def main() -> None:
    frame = load()
    report = {
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "duplicate_rows": int(frame.duplicated().sum()),
        "unique_patient_ids": int(frame["Patient ID"].nunique()),
        "age_in_months": {
            "minimum": int(frame["Age in months"].min()),
            "maximum": int(frame["Age in months"].max()),
            "above_article_stated_14_year_limit_n": int((frame["Age in months"] > 168).sum()),
            "note": "The publication states ages 1–14 years; preserve and flag source rows above 168 months for sensitivity review.",
        },
        "target_counts": {
            str(k): int(v)
            for k, v in frame["DSM 5 gold standard diagnosis"].value_counts(dropna=False).items()
        },
        "fields": {},
        "label_definition": "DSM-5 gold-standard diagnosis; paper reports 128 ASD and 97 non-ASD among 225, matching encoded 1 and 2 counts respectively.",
        "provenance": "PLOS ONE 2019 S2 deidentified dataset; Figshare article 7840055; CC BY 4.0.",
        "leakage_exclusions": [
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
            "DP3 fields",
        ],
        "compatibility": "The 28 AIIMS Modified INDT-ASD items and DSM-5 expert target differ from UCI A1-A10/threshold-derived Class. Analyze separately; do not pool or directly compare metrics.",
    }
    for column in frame:
        series = frame[column]
        report["fields"][column] = {
            "dtype": str(series.dtype),
            "missing": int(series.isna().sum()),
            "unique_count": int(series.nunique(dropna=True)),
            "values": [str(value) for value in series.dropna().unique()[:60]],
        }
    out = ROOT / "experiments/reports/indian_data_quality.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(f"Wrote {out}; {len(frame)} rows, {len(frame.columns)} columns")


if __name__ == "__main__":
    main()
