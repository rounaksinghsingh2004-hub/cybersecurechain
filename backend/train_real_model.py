import os
import glob
import time
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

def clean_label(label_str):
    s = str(label_str).strip()
    if "Web Attack" in s:
        if "Brute" in s or "Force" in s:
            return "Web Attack - Brute Force"
        elif "XSS" in s:
            return "Web Attack - XSS"
        elif "Sql" in s or "SQL" in s:
            return "Web Attack - SQL Injection"
        return "Web Attack"
    if "DDoS" in s:
        return "DDoS"
    if "PortScan" in s:
        return "PortScan"
    if "Bot" in s:
        return "Bot"
    if "Infiltration" in s:
        return "Infiltration"
    if "FTP-Patator" in s:
        return "FTP-Patator"
    if "SSH-Patator" in s:
        return "SSH-Patator"
    if "DoS slowloris" in s:
        return "DoS Slowloris"
    if "DoS Slowhttptest" in s:
        return "DoS Slowhttptest"
    if "DoS Hulk" in s:
        return "DoS Hulk"
    if "DoS GoldenEye" in s:
        return "DoS GoldenEye"
    if "Heartbleed" in s:
        return "Heartbleed"
    if "BENIGN" in s.upper():
        return "BENIGN"
    return s.encode('ascii', 'ignore').decode('ascii').strip() or "Unknown"

def train_real_ids_model(dataset_dir: str):
    print(f"Loading and processing dataset from {dataset_dir}...", flush=True)
    csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {dataset_dir}")

    df_list = []
    t0 = time.time()
    for file in csv_files:
        fname = os.path.basename(file)
        try:
            header = [c.strip() for c in pd.read_csv(file, nrows=0).columns]
            df_chunk = pd.read_csv(file, on_bad_lines='skip', low_memory=False)
            df_chunk.columns = header
            if 'Label' in df_chunk.columns:
                attacks = df_chunk[df_chunk['Label'] != 'BENIGN']
                benigns = df_chunk[df_chunk['Label'] == 'BENIGN']
                sampled_attacks = attacks.sample(n=min(len(attacks), 12000), random_state=42) if len(attacks) > 0 else attacks
                sampled_benigns = benigns.sample(n=min(len(benigns), 8000), random_state=42) if len(benigns) > 0 else benigns
                df_list.append(pd.concat([sampled_attacks, sampled_benigns]))
                print(f"  [{fname}] -> {len(sampled_attacks)} attack, {len(sampled_benigns)} benign samples", flush=True)
        except Exception as e:
            print(f"  Error reading {fname}: {e}", flush=True)

    df = pd.concat(df_list, ignore_index=True)
    df['Clean_Label'] = df['Label'].apply(clean_label)

    # Filter out rare singletons (e.g. Heartbleed with 1 row) for robust stratified splitting
    valid_classes = df['Clean_Label'].value_counts()[lambda x: x >= 10].index
    df = df[df['Clean_Label'].isin(valid_classes)].copy()

    drop_cols = ['Label', 'Clean_Label']
    feature_cols = [c for c in df.columns if c not in drop_cols]
    
    X = df[feature_cols].copy()
    y = df['Clean_Label'].copy()

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors='coerce')
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"\nTraining high-performance RandomForestClassifier (30 trees, max_depth=14)...", flush=True)
    model = RandomForestClassifier(n_estimators=30, max_depth=14, random_state=42, n_jobs=1)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    print(f"Model validation accuracy on test set: {score*100:.2f}%", flush=True)

    target_dir = os.path.join(os.path.dirname(__file__), "app", "simulation")
    model_path = os.path.join(target_dir, "real_ids_model.pkl")
    features_path = os.path.join(target_dir, "real_ids_features.pkl")

    model.n_jobs = 1
    joblib.dump(model, model_path, compress=3)
    joblib.dump(list(X.columns), features_path)
    print(f"Trained IDS ML Model saved successfully to: {model_path} ({os.path.getsize(model_path)/1024:.1f} KB)", flush=True)

if __name__ == "__main__":
    dataset_path = r"C:\Users\rouna\Downloads\MachineLearningCSV\MachineLearningCVE"
    train_real_ids_model(dataset_path)
