"""Download ViCoS BJJ dataset (images + annotations)."""

import os
import urllib.request
import zipfile
from pathlib import Path

IMAGES_URL = "http://data.vicos.si/datasets/JuiJuitsu/images.zip"
ANNOTATIONS_URL = "http://data.vicos.si/datasets/JuiJuitsu/annotations.json"

DATA_DIR = Path(__file__).parent


def download_file(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"Already exists: {dest}")
        return
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)
    print(f"Saved to {dest}")


def extract_zip(zip_path: Path, extract_to: Path) -> None:
    if extract_to.exists() and any(extract_to.iterdir()):
        print(f"Already extracted: {extract_to}")
        return
    print(f"Extracting {zip_path} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    print(f"Extracted to {extract_to}")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    annotations_path = DATA_DIR / "annotations.json"
    download_file(ANNOTATIONS_URL, annotations_path)

    zip_path = DATA_DIR / "images.zip"
    download_file(IMAGES_URL, zip_path)

    images_dir = DATA_DIR / "images"
    extract_zip(zip_path, images_dir)

    print("Done. Dataset ready in data/")


if __name__ == "__main__":
    main()
