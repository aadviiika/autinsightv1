"""Generate source-data charts for the independent AIIMS validation cohort."""

from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from validate_indian_data import load

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    frame = load()
    reports, figures = ROOT / "experiments/reports", ROOT / "experiments/figures"
    reports.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    summary = {
        "rows": len(frame),
        "columns": len(frame.columns),
        "target_counts": {
            str(k): int(v) for k, v in frame["DSM 5 gold standard diagnosis"].value_counts().items()
        },
        "missing": {str(k): int(v) for k, v in frame.isna().sum().items() if v},
        "duplicates": int(frame.duplicated().sum()),
    }
    (reports / "indian_eda_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 4))
    frame["DSM 5 gold standard diagnosis"].value_counts().sort_index().plot.bar(
        ax=ax, color="#0d6b63"
    )
    ax.set(
        title="Indian validation cohort: DSM-5 gold-standard labels",
        xlabel="Source code (1=ASD, 2=non-ASD)",
        ylabel="Children",
    )
    fig.tight_layout()
    fig.savefig(figures / "indian_target_distribution.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    pd.to_numeric(frame["Age in months"], errors="coerce").hist(ax=ax, bins=15, color="#477d9a")
    ax.set(title="Age in months: AIIMS validation cohort", xlabel="Age (months)", ylabel="Children")
    fig.tight_layout()
    fig.savefig(figures / "indian_age_distribution.png", dpi=160)
    plt.close(fig)
    missing = frame.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    fig, ax = plt.subplots(figsize=(10, 4))
    missing.plot.bar(ax=ax, color="#d29452")
    ax.set(
        title="Missing fields in Indian validation cohort",
        xlabel="Source field",
        ylabel="Missing records",
    )
    fig.tight_layout()
    fig.savefig(figures / "indian_missingness.png", dpi=160)
    plt.close(fig)
    print(f"Indian EDA written to {ROOT / 'experiments'}")


if __name__ == "__main__":
    main()
