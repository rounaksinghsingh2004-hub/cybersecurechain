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

def clean_label(label_str):
    s = str(label_str).strip()
    s_clean = s.encode('ascii', errors='ignore').decode('ascii').strip()
    if "BENIGN" in s.upper():
        return "BENIGN"
    if "DDoS" in s or "DDOS" in s:
        return "DDoS"
    if "PortScan" in s or "Port Scan" in s:
        return "PortScan"
    if "Bot" in s:
        return "Bot"
    if "Infiltration" in s or "Infilteration" in s:
        return "Infiltration"
    if "FTP-Patator" in s:
        return "FTP-Patator"
    if "SSH-Patator" in s:
        return "SSH-Patator"
    if "slowloris" in s.lower():
        return "DoS Slowloris"
    if "slowhttptest" in s.lower():
        return "DoS Slowhttptest"
    if "hulk" in s.lower():
        return "DoS Hulk"
    if "goldeneye" in s.lower():
        return "DoS GoldenEye"
    if "Heartbleed" in s:
        return "Heartbleed"
    if "Web Attack" in s:
        if "Brute" in s:
            return "Web Attack - Brute Force"
        elif "XSS" in s:
            return "Web Attack - XSS"
        elif "Sql" in s or "SQL" in s:
            return "Web Attack - SQL Injection"
        return "Web Attack"
    return s_clean or "Unknown"

def load_full_dataset(dataset_dir: str) -> pd.DataFrame:
    print(f"[*] Discovering dataset CSV files in: {dataset_dir}", flush=True)
    csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {dataset_dir}")
    
    print(f"[*] Found {len(csv_files)} files. Loading full dataset into memory (zero dropped rows)...", flush=True)
    dfs = []
    total_raw_rows = 0
    t0 = time.time()
    
    for fpath in csv_files:
        fname = os.path.basename(fpath)
        # Robust loading: cp1252 handles any Windows/Latin byte quirks without skipping lines
        df_chunk = pd.read_csv(fpath, encoding='cp1252', low_memory=False)
        df_chunk.columns = [c.strip() for c in df_chunk.columns]
        dfs.append(df_chunk)
        total_raw_rows += len(df_chunk)
        print(f"    + [{fname}] loaded {len(df_chunk):,d} rows", flush=True)
        
    print(f"[*] Concatenating all files into single master dataset...", flush=True)
    full_df = pd.concat(dfs, ignore_index=True)
    del dfs
    gc.collect()
    
    print(f"[*] Master dataset ready: {len(full_df):,d} rows across {len(full_df.columns)} columns in {time.time()-t0:.1f}s", flush=True)
    return full_df

def extract_attack_prototypes(df: pd.DataFrame, feature_cols: list[str], target_dir: str):
    """
    Extract genuine packet feature signatures for all attack classes from the real dataset.
    This enables the live simulator to inject 100% authentic CIC-IDS2017 network traffic.
    """
    print(f"[*] Extracting authentic attack prototypes across all attack classes...", flush=True)
    prototypes = {}
    
    for label in df['Clean_Label'].unique():
        if label == "BENIGN" or label == "Unknown":
            continue
        sub = df[df['Clean_Label'] == label]
        if len(sub) == 0:
            continue
        # Compute median feature profile for the attack class
        median_feats = sub[feature_cols].median().to_dict()
        prototypes[label] = {k: float(v) for k, v in median_feats.items()}
        print(f"    - Prototype for '{label}' extracted from {len(sub):,d} genuine flows", flush=True)
        
    proto_path = os.path.join(target_dir, "attack_prototypes.pkl")
    joblib.dump(prototypes, proto_path, compress=3)
    print(f"[+] Saved {len(prototypes)} authentic attack prototypes to: {proto_path}", flush=True)
    return prototypes

def preprocess_and_clean(df: pd.DataFrame):
    print(f"[*] Preprocessing and cleaning dataset (fixing all failed / inf / nan data)...", flush=True)
    df['Clean_Label'] = df['Label'].apply(clean_label)
    
    drop_cols = ['Label', 'Clean_Label']
    feature_cols = [c for c in df.columns if c not in drop_cols]
    
    print(f"[*] Sanitizing {len(feature_cols)} feature columns to float32 without discarding rows...", flush=True)
    X = df[feature_cols].copy()
    y = df['Clean_Label'].copy()
    
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors='coerce').astype(np.float32)
        # Fix infinite values (Flow Bytes/s, Flow Packets/s) by capping to max finite value
        finite_mask = np.isfinite(X[col])
        max_val = X.loc[finite_mask, col].max() if finite_mask.any() else 0.0
        X[col] = X[col].replace([np.inf], max_val).replace([-np.inf], 0.0).fillna(0.0)
        
    print(f"[*] Class distribution across entire 100% dataset ({len(y):,d} samples):", flush=True)
    for lbl, count in y.value_counts().items():
        print(f"    - {lbl:26s}: {count:9,d} ({count/len(y)*100:6.3f}%)", flush=True)
        
    return X, y, feature_cols

def train_and_save_model(X: pd.DataFrame, y: pd.Series, feature_cols: list[str], target_dir: str):
    print(f"\n[*] Splitting 80% train / 20% test with stratified balance across all 15 classes...", flush=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[*] Training set: {len(X_train):,d} samples | Test set: {len(X_test):,d} samples", flush=True)
    
    print(f"[*] Fitting high-performance RandomForestClassifier (60 trees, max_depth=18, balanced weights)...", flush=True)
    t_train = time.time()
    model = RandomForestClassifier(
        n_estimators=60,
        max_depth=18,
        min_samples_split=5,
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    train_duration = time.time() - t_train
    print(f"[+] Model trained in {train_duration:.1f} seconds!", flush=True)
    
    print(f"[*] Evaluating model on unseen test set ({len(X_test):,d} flows)...", flush=True)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[+] Overall Test Set Accuracy: {acc*100:.3f}%\n", flush=True)
    
    print("=== CLASSIFICATION REPORT (WHOLE CIC-IDS2017 DATASET) ===", flush=True)
    report = classification_report(y_test, y_pred, digits=4, zero_division=0)
    print(report, flush=True)
    
    # Save model and features
    model_path = os.path.join(target_dir, "real_ids_model.pkl")
    features_path = os.path.join(target_dir, "real_ids_features.pkl")
    
    # Single-thread model before serialization for portable serving
    model.n_jobs = 1
    joblib.dump(model, model_path, compress=3)
    joblib.dump(feature_cols, features_path)
    
    print(f"[+] Model saved to: {model_path} ({os.path.getsize(model_path)/(1024*1024):.2f} MB)", flush=True)
    print(f"[+] Features list saved to: {features_path} ({len(feature_cols)} features)", flush=True)

def main():
    dataset_dir = r"C:\Users\rouna\Downloads\MachineLearningCSV\MachineLearningCVE"
    target_dir = os.path.join(os.path.dirname(__file__), "app", "simulation")
    
    full_df = load_full_dataset(dataset_dir)
    X, y, feature_cols = preprocess_and_clean(full_df)
    
    # Extract authentic prototypes for live simulation
    extract_attack_prototypes(full_df, feature_cols, target_dir)
    
    # Free raw DataFrame to conserve RAM for training
    del full_df
    gc.collect()
    
    # Train and serialize model
    train_and_save_model(X, y, feature_cols, target_dir)
    print("\n[SUCCESS] Full CIC-IDS2017 dataset pipeline completed successfully!", flush=True)

if __name__ == "__main__":
    main()
