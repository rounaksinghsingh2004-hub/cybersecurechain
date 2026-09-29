import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

def generate_synthetic_data(num_samples=5000):
    np.random.seed(42)
    
    # Features
    affected_assets = np.random.randint(1, 100, num_samples)
    affected_orders = np.random.randint(0, 500, num_samples)
    
    # Introduce realistic non-linearity and operational variance
    downtime_minutes = (affected_assets * 18) * np.random.normal(1.0, 0.1, num_samples) + np.random.randint(0, 60, num_samples)
    estimated_revenue_loss = (affected_orders * 2800) * np.random.normal(1.0, 0.15, num_samples) + (affected_assets * 500)
    recovery_cost = (affected_assets * 15000) * np.random.normal(1.0, 0.1, num_samples) + np.random.randint(5000, 20000, num_samples)
    
    df = pd.DataFrame({
        'affected_assets': affected_assets,
        'affected_orders': affected_orders,
        'downtime_minutes': downtime_minutes.astype(int),
        'estimated_revenue_loss': estimated_revenue_loss.astype(int),
        'recovery_cost': recovery_cost.astype(int)
    })
    
    df['downtime_minutes'] = df['downtime_minutes'].clip(lower=0)
    df['estimated_revenue_loss'] = df['estimated_revenue_loss'].clip(lower=0)
    df['recovery_cost'] = df['recovery_cost'].clip(lower=0)
    
    return df

def main():
    print("Generating training data for business impact regression...", flush=True)
    df = generate_synthetic_data()
    
    X = df[['affected_assets', 'affected_orders']]
    y = df[['downtime_minutes', 'estimated_revenue_loss', 'recovery_cost']]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training optimized RandomForestRegressor model...", flush=True)
    model = RandomForestRegressor(n_estimators=30, max_depth=8, random_state=42, n_jobs=1)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    print(f"Model R^2 score on test set: {score:.4f}", flush=True)
    
    model.n_jobs = 1
    model_path = os.path.join(os.path.dirname(__file__), "app", "simulation", "ml_model.pkl")
    joblib.dump(model, model_path, compress=3)
    print(f"Model saved to {model_path} ({os.path.getsize(model_path)/1024:.1f} KB)", flush=True)

if __name__ == "__main__":
    main()
