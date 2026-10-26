"""Generate exploratory tables and plots from the locally acquired primary data."""

from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from validate_data import load

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments"


def main() -> None:
    frame = load().copy()
    figures = OUT / "figures"
    reports = OUT / "reports"
    figures.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    lower = {str(c).lower().strip(): c for c in frame.columns}
    target = next(
        (lower[k] for k in ("class/asd", "class_asd", "class", "asd") if k in lower), None
    )
    if not target:
        raise SystemExit("No target candidate found; inspect source schema.")
    summary = {
        "rows": len(frame),
        "columns": len(frame.columns),
        "missing": frame.isna().sum().astype(int).to_dict(),
        "duplicates": int(frame.duplicated().sum()),
        "target_counts": frame[target].value_counts(dropna=False).astype(int).to_dict(),
    }
    (reports / "eda_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4))
    frame[target].astype(str).value_counts().plot.bar(ax=ax, color="#0d6b63")
    ax.set(title="Observed screening class counts", xlabel="Source class", ylabel="Records")
    fig.tight_layout()
    fig.savefig(figures / "class_distribution.png", dpi=160)
    plt.close(fig)
    missing = frame.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    if len(missing):
        fig, ax = plt.subplots(figsize=(9, 4))
        missing.plot.bar(ax=ax, color="#d29452")
        ax.set(title="Missing values by source field", ylabel="Missing records", xlabel="Field")
        fig.tight_layout()
        fig.savefig(figures / "missingness.png", dpi=160)
        plt.close(fig)
    age_col = lower.get("age")
    if age_col:
        age = pd.to_numeric(frame[age_col], errors="coerce").dropna()
        fig, ax = plt.subplots(figsize=(7, 4))
        age.hist(ax=ax, bins=15, color="#5a8f86")
        ax.set(
            title="Observed age distribution", xlabel="Age (source units; verify)", ylabel="Records"
        )
        fig.tight_layout()
        fig.savefig(figures / "age_distribution.png", dpi=160)
        plt.close(fig)
    qcols = [lower.get(f"a{i}_score") for i in range(1, 11) if f"a{i}_score" in lower]
    if qcols:
        responses = frame[qcols].apply(pd.to_numeric, errors="coerce").mean().sort_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        responses.plot.bar(ax=ax, color="#477d9a")
        ax.set(
            title="Mean observed questionnaire response",
            ylabel="Mean response code",
            xlabel="Source item",
        )
        fig.tight_layout()
        fig.savefig(figures / "questionnaire_response_means.png", dpi=160)
        plt.close(fig)
    print(f"EDA output written to {OUT}")


if __name__ == "__main__":
    main()
