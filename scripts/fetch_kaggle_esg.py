"""Download a CSV from a Kaggle dataset using the Kaggle API.

Requires KAGGLE_USERNAME and KAGGLE_KEY in env or from .env.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import zipfile

from kaggle.api.kaggle_api_extended import KaggleApi


def main():
    parser = argparse.ArgumentParser(description="Fetch Kaggle ESG dataset")
    parser.add_argument("--dataset", default="therohk/global-esg-scores-2021")
    parser.add_argument("--file", default=None)
    parser.add_argument("--out", default="data/raw/kaggle_esg.csv")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as e:
        print("Failed to authenticate with Kaggle. Ensure KAGGLE_USERNAME and KAGGLE_KEY are set.")
        raise

    try:
        files = api.dataset_list_files(args.dataset)
        file_names = [f.name for f in files.files]
    except Exception as e:
        print(f"Failed to list files for dataset {args.dataset}: {e}")
        return

    target = args.file or next((n for n in file_names if n.endswith('.csv')), None)
    if target is None:
        print("No CSV file found in the dataset. Please specify --file explicitly.")
        return

    # download file to a temp dir
    try:
        api.dataset_download_file(args.dataset, file_name=target, path=out_path.parent, force=True)
        z = out_path.parent / (target + ".zip")
        # The Kaggle API saves zipped file with .zip when single file
        if z.exists():
            with zipfile.ZipFile(z, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.csv'):
                        zf.extract(name, out_path.parent)
                        extracted = out_path.parent / name
                        extracted.rename(out_path)
                        z.unlink()
                        break
        print(f"Saved Kaggle CSV to {out_path}")
    except Exception as e:
        print(f"Failed to download or extract file: {e}")


if __name__ == "__main__":
    main()
