"""Acquire the licensed UCI dataset via its official repository API."""

from pathlib import Path
import hashlib
import json
import ssl
import certifi
from datetime import date

from ucimlrepo import fetch_ucirepo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
RAW.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
    dataset = fetch_ucirepo(id=419)
    frame = dataset.data.original
    if frame is None or frame.empty:
        raise SystemExit(
            "UCI returned no original rows; see data/README.md for manual instructions."
        )
    out = RAW / "uci_asd_children.csv"
    frame.to_csv(out, index=False)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    metadata = {
        "source": "https://archive.ics.uci.edu/dataset/419/autistic+spectrum+disorder+screening+data+for+children",
        "retrieved": date.today().isoformat(),
        "dataset_id": 419,
        "license": "CC BY 4.0",
        "filename": out.name,
        "sha256": digest,
        "rows": len(frame),
        "columns": list(frame.columns),
    }
    (RAW / "provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
