"""Acquire the publicly released deidentified AIIMS modified INDT-ASD S2 workbook."""

from pathlib import Path
from datetime import date
import hashlib
import json
import ssl
import urllib.request
import certifi

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_ID = "7840055"
RAW = ROOT / "data/raw"


def main() -> None:
    context = ssl.create_default_context(cafile=certifi.where())
    metadata_url = f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
    with urllib.request.urlopen(metadata_url, context=context, timeout=30) as response:
        article = json.load(response)
    if article.get("doi") != "10.1371/journal.pone.0213242":
        raise SystemExit("Figshare DOI does not match the cited PLOS validation study.")
    license_info = article.get("license") or {}
    if license_info.get("name") != "CC BY 4.0":
        raise SystemExit(f"Unexpected dataset license: {license_info}")
    file_info = next(
        (item for item in article.get("files", []) if item.get("name", "").endswith("s002.xlsx")),
        None,
    )
    if not file_info:
        raise SystemExit("Expected S2 deidentified dataset workbook is not present.")
    RAW.mkdir(parents=True, exist_ok=True)
    output = RAW / "aiims_modified_indt_asd_s2.xlsx"
    with urllib.request.urlopen(file_info["download_url"], context=context, timeout=30) as response:
        content = response.read()
    output.write_bytes(content)
    digest = hashlib.md5(content).hexdigest()
    if digest != file_info.get("computed_md5"):
        output.unlink(missing_ok=True)
        raise SystemExit("Downloaded workbook checksum does not match Figshare metadata.")
    manifest = {
        "source_article": "https://doi.org/10.1371/journal.pone.0213242",
        "repository_url": article["url"],
        "retrieved": date.today().isoformat(),
        "license": license_info["name"],
        "filename": output.name,
        "figshare_file_id": file_info["id"],
        "size_bytes": len(content),
        "md5": digest,
        "article_title": article["title"],
    }
    (RAW / "indian_provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
