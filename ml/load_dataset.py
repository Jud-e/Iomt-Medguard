"""
Loads the CICIDS2017 MachineLearningCSV files into one combined DataFrame,
ready for feature extraction / Isolation Forest training.

Expects files extracted from MachineLearningCSV.zip (download instructions:
see README.md) sitting in ingestion/datasets/cicids2017/*.csv

Handles three known quirks in these specific files:
1. Column names have leading/trailing whitespace (e.g. " Label", " Flow Duration")
   -> stripped on load, so `df["Label"]` works instead of `df[" Label"]`.
2. "Flow Bytes/s" and "Flow Packets/s" contain Infinity and NaN values for
   flows with ~0 duration -> these rows are dropped by default (see
   drop_invalid) rather than silently poisoning model training.
3. Files are split one-per-weekday -> this loads and concatenates all of them.

Run directly for a sanity check:
    python load_dataset.py
"""
from pathlib import Path
from typing import Optional

import pandas as pd

DATASET_DIR = Path(__file__).parent.parent / "ingestion" / "datasets" / "cicids2017"


def load_cicids2017(dataset_dir: Optional[Path] = None, drop_invalid: bool = True) -> pd.DataFrame:
    dataset_dir = dataset_dir or DATASET_DIR
    csv_files = sorted(dataset_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {dataset_dir}. "
            f"Download MachineLearningCSV.zip from http://cicresearch.ca/CICDataset/CIC-IDS-2017/ "
            f"and extract it here first."
        )

    print(f"Found {len(csv_files)} CSV file(s) in {dataset_dir}:")
    frames = []
    for path in csv_files:
        df = pd.read_csv(path, low_memory=False)
        df.columns = df.columns.str.strip()  # quirk #1
        print(f"  {path.name}: {len(df):,} rows")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    # quirk #4: a handful of Web Attack labels in the original CIC files
    # contain a mangled en-dash (shows up as "�") — cosmetic only, doesn't
    # affect training since the strings are still internally consistent,
    # but cleaned up here so reports/plots don't show a broken character.
    combined["Label"] = combined["Label"].str.replace("\ufffd", "-", regex=False)

    if drop_invalid:
        before = len(combined)
        combined = combined.replace([float("inf"), float("-inf")], pd.NA).dropna(
            subset=["Flow Bytes/s", "Flow Packets/s"]
        )
        dropped = before - len(combined)
        if dropped:
            print(f"Dropped {dropped:,} rows with Infinity/NaN in Flow Bytes/s or Flow Packets/s")

    print(f"\nTotal: {len(combined):,} rows, {combined.shape[1]} columns")
    print(f"Label distribution:\n{combined['Label'].value_counts()}")

    return combined


def split_train_eval(df: pd.DataFrame):
    """
    Isolation Forest should train on BENIGN traffic only, not the full
    mixed dataset. Reason: the algorithm flags points that are rare/isolated
    in feature space. Large attack classes in this dataset (DoS Hulk:
    230k+ rows, PortScan: 158k+, DDoS: 128k+) are NOT rare — trained on the
    full mix, the model would likely learn them as "normal" rather than
    flag them, since isolation-based detection has no concept of a Label
    column telling it otherwise.

    Returns:
        train_df: BENIGN rows only -> fit the model on this
        eval_df:  ALL rows, with a binary `is_attack` column -> score
                  the fitted model against this to compute precision/recall
    """
    train_df = df[df["Label"] == "BENIGN"].drop(columns=["Label"]).reset_index(drop=True)

    eval_df = df.copy()
    eval_df["is_attack"] = (eval_df["Label"] != "BENIGN").astype(int)

    print(f"\nTrain set (BENIGN only): {len(train_df):,} rows")
    print(f"Eval set (all labels):   {len(eval_df):,} rows "
          f"({eval_df['is_attack'].sum():,} attack / {(eval_df['is_attack'] == 0).sum():,} benign)")

    return train_df, eval_df


if __name__ == "__main__":
    df = load_cicids2017()
    print("\nColumn names:")
    print(list(df.columns))

    train_df, eval_df = split_train_eval(df)