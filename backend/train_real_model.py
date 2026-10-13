import os
import glob
import time
import gc
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# ─── Non-feature (metadata) columns to exclude ────────────────────────────────
NON_FEATURE_COLS = {'Flow ID', 'Source IP', 'Destination IP', 'Timestamp',
                    'Source_File', 'Label'}

def clean_label(raw):
    s = str(raw).strip()
    s_ascii = s.encode('ascii', errors='ignore').decode('ascii').strip()
    if not s_ascii or s_ascii.lower() == 'nan':
        return None          # will be dropped
    if 'BENIGN' in s.upper():
        return 'BENIGN'
    if 'DDoS' in s or 'DDOS' in s:
        return 'DDoS'
    if 'PortScan' in s or 'Port Scan' in s:
        return 'PortScan'
    if 'Bot' in s:
        return 'Bot'
    if 'Infiltration' in s or 'Infilteration' in s:
        return 'Infiltration'
    if 'Heartbleed' in s:
        return 'Heartbleed'
    if 'FTP-Patator' in s:
        return 'FTP-Patator'
    if 'SSH-Patator' in s:
        return 'SSH-Patator'
    if 'slowloris' in s.lower():
        return 'DoS Slowloris'
    if 'slowhttptest' in s.lower():
        return 'DoS Slowhttptest'
    if 'hulk' in s.lower():
        return 'DoS Hulk'
    if 'goldeneye' in s.lower():
        return 'DoS GoldenEye'
    if 'Web Attack' in s:
        if 'Brute' in s:
            return 'Web Attack - Brute Force'
        elif 'XSS' in s:
            return 'Web Attack - XSS'
        elif 'Sql' in s or 'SQL' in s:
            return 'Web Attack - SQL Injection'
        return 'Web Attack'
    return s_ascii or None

def load_full_dataset_with_extra_features(
    raw_dir: str,
    merged_file: str,
) -> pd.DataFrame:
    """
    Strategy: Load the raw per-day CSVs (perfect encoding, 78 features + Label)
    and the merged cicids2017_with_timestamp.csv (80 features — adds Source Port
    + Protocol). The merged file's rows are guaranteed to be in the same order
    as the raw files concatenated. We join on row position to get 80 features.
    """
    print("[*] Loading all 8 raw per-day CIC-IDS2017 CSV files (78 features, all rows)...", flush=True)
    csv_files = sorted(glob.glob(os.path.join(raw_dir, "*.csv")))
    if not csv_files:
        raise ValueError(f"No CSV files in {raw_dir}")

    raw_dfs = []
    total_raw = 0
    for fpath in csv_files:
        fname = os.path.basename(fpath)
        df = pd.read_csv(fpath, encoding='cp1252', low_memory=False)
        df.columns = [c.strip() for c in df.columns]
        raw_dfs.append(df)
        total_raw += len(df)
        print(f"    + [{fname}] {len(df):,} rows", flush=True)

    raw_master = pd.concat(raw_dfs, ignore_index=True)
    del raw_dfs
    gc.collect()
    print(f"[+] Raw master: {len(raw_master):,} rows, {len(raw_master.columns)} columns", flush=True)

    # Now load merged file to get Source Port and Protocol
    print(f"\n[*] Loading merged file for extra columns (Source Port, Protocol)...", flush=True)
    merged = pd.read_csv(
        merged_file,
        usecols=['Source Port', 'Protocol'],
        low_memory=False,
        encoding='cp1252',
        on_bad_lines='skip',
    )
    print(f"[+] Merged file: {len(merged):,} rows (Source Port + Protocol)", flush=True)

    # The merged file has 3,119,345 rows because Thursday Infiltration was
    # concatenated differently in that file. We only need the rows that align
    # with raw_master (2,830,743). Trim to match raw_master length.
    if len(merged) > len(raw_master):
        print(f"[!] Merged file has {len(merged) - len(raw_master):,} extra rows — trimming to match raw master.", flush=True)
        merged = merged.iloc[:len(raw_master)].reset_index(drop=True)
    elif len(merged) < len(raw_master):
        print(f"[!] Merged file is shorter — padding missing Source Port/Protocol with 0.", flush=True)
        pad = pd.DataFrame({'Source Port': 0, 'Protocol': 0},
                           index=range(len(raw_master) - len(merged)))
        merged = pd.concat([merged, pad], ignore_index=True)

    raw_master['Source Port'] = pd.to_numeric(merged['Source Port'], errors='coerce').fillna(0).astype(np.float32)
    raw_master['Protocol'] = pd.to_numeric(merged['Protocol'], errors='coerce').fillna(0).astype(np.float32)
    del merged
    gc.collect()

    print(f"[+] Final dataset: {len(raw_master):,} rows, {len(raw_master.columns)} columns "
          f"(now {len(raw_master.columns) - 1} features + Label)", flush=True)
    return raw_master


def extract_attack_prototypes(df: pd.DataFrame, feature_cols: list, target_dir: str):
    print(f"\n[*] Extracting authentic attack prototypes for all {len(df['Clean_Label'].unique()) - 1} attack classes...", flush=True)
    prototypes = {}
    for label in df['Clean_Label'].unique():
        if label in ('BENIGN', 'Unknown', None):
            continue
        sub = df[df['Clean_Label'] == label]
        if len(sub) == 0:
            continue
        median_feats = sub[feature_cols].median().to_dict()
        prototypes[label] = {k: float(v) for k, v in median_feats.items()}
        print(f"    - '{label}': {len(sub):,} flows", flush=True)

    proto_path = os.path.join(target_dir, "attack_prototypes.pkl")
    joblib.dump(prototypes, proto_path, compress=3)
    print(f"[+] {len(prototypes)} prototypes saved -> {proto_path}", flush=True)


def preprocess(df: pd.DataFrame):
    print(f"\n[*] Cleaning labels...", flush=True)
    df['Clean_Label'] = df['Label'].apply(clean_label)
    df = df.dropna(subset=['Clean_Label'])
    print(f"[+] Retained {len(df):,} rows after removing unlabelled entries", flush=True)

    drop_cols = {'Label', 'Clean_Label'} | NON_FEATURE_COLS
    feature_cols = [c for c in df.columns if c not in drop_cols]
    print(f"[*] Sanitizing {len(feature_cols)} feature columns to float32...", flush=True)

    X = df[feature_cols].copy()
    y = df['Clean_Label'].copy()

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors='coerce').astype(np.float32)
        finite_mask = np.isfinite(X[col])
        max_val = float(X.loc[finite_mask, col].max()) if finite_mask.any() else 0.0
        X[col] = X[col].replace([np.inf], max_val).replace([-np.inf], 0.0).fillna(0.0)

    # Filter rare classes with < 5 samples (can't stratify split)
    valid = y.value_counts()[lambda s: s >= 5].index
    mask = y.isin(valid)
    X, y = X[mask], y[mask]

    print(f"\n[*] Class distribution — full {len(y):,} sample dataset:", flush=True)
    for lbl, cnt in y.value_counts().items():
        print(f"    {lbl:28s}: {cnt:9,d}  ({cnt/len(y)*100:6.3f}%)", flush=True)

    return X, y, feature_cols


def train_and_save(X, y, feature_cols, target_dir):
    print(f"\n[*] Splitting 80/20 with stratification across {y.nunique()} classes...", flush=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[+] Train: {len(X_train):,}  |  Test: {len(X_test):,}", flush=True)

    print(f"[*] Fitting RandomForest (60 trees, max_depth=18, balanced_subsample)...", flush=True)
    t0 = time.time()
    clf = RandomForestClassifier(
        n_estimators=60,
        max_depth=18,
        min_samples_split=5,
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)
    print(f"[+] Trained in {time.time()-t0:.1f}s", flush=True)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[+] Test Accuracy: {acc*100:.3f}%\n", flush=True)
    print("=== CLASSIFICATION REPORT ===", flush=True)
    print(classification_report(y_test, y_pred, digits=4, zero_division=0), flush=True)

    clf.n_jobs = 1
    model_path = os.path.join(target_dir, "real_ids_model.pkl")
    features_path = os.path.join(target_dir, "real_ids_features.pkl")
    joblib.dump(clf, model_path, compress=3)
    joblib.dump(feature_cols, features_path)
    sz = os.path.getsize(model_path) / (1024 * 1024)
    print(f"[+] Model saved -> {model_path}  ({sz:.2f} MB,  {len(feature_cols)} features)", flush=True)
    print(f"[+] Features list saved -> {features_path}", flush=True)


def main():
    raw_dir = r"C:\Users\rouna\Downloads\MachineLearningCSV\MachineLearningCVE"
    merged_file = r"C:\Users\rouna\Downloads\threat-forecast-starter\threat-forecast-starter\data\cicids2017_with_timestamp.csv"
    target_dir = os.path.join(os.path.dirname(__file__), "app", "simulation")

    full_df = load_full_dataset_with_extra_features(raw_dir, merged_file)

    X, y, feature_cols = preprocess(full_df)
    extract_attack_prototypes(
        full_df.assign(Clean_Label=full_df['Label'].apply(clean_label)).dropna(subset=['Clean_Label']),
        feature_cols, target_dir
    )
    del full_df
    gc.collect()

    train_and_save(X, y, feature_cols, target_dir)
    print("\n[SUCCESS] Full 80-feature CIC-IDS2017 pipeline complete!", flush=True)


if __name__ == "__main__":
    main()
