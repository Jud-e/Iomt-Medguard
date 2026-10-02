# Datasets

Neither dataset is committed to this repo — both are large and are gitignored.
Download them yourself and place the extracted files in the matching folder
below. Loaded by `../../ml/load_dataset.py`.

## CICIDS2017 → `cicids2017/`

1. Go to http://cicresearch.ca/CICDataset/CIC-IDS-2017/ (official UNB/CIC
   mirror, no login or registration required).
2. Download **`MachineLearningCSV.zip`** specifically — not the `.pcap`
   files. The CSV zip is pre-processed, labeled flow data (already run
   through CICFlowMeter); the PCAPs are 50GB+ of raw packet captures you'd
   have to extract features from yourself.
3. Extract it — you'll get one `.csv` per weekday (Monday = benign traffic
   only, Tuesday–Friday = benign + labeled attacks).
4. Place the extracted `.csv` files directly in `cicids2017/`.

## ECU-IoHT → `ecu-ioht/`

1. Go to https://ro.ecu.edu.au/datasets/48 — open access, no request form.
2. Download and extract the files directly into `ecu-ioht/`.

Note: your project brief refers to this as "ECU IoMT" — the dataset's actual
published name is ECU-IoHT (Internet of *Health* Things), Ahmed et al. 2021.

## After downloading

Run a sanity check:
```bash
python ../../ml/load_dataset.py
```
This loads every CSV in `cicids2017/`, strips known formatting quirks
(leading-space column names, Infinity/NaN values in a couple of columns),
and prints row counts plus the label distribution.

When you get to `train_isolation_forest.py`, your code should call `split_train_eval(df)` and fit the model on `train_df`, then score `eval_df` and check `is_attack` against what the model flagged.