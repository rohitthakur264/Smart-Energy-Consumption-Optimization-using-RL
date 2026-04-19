import os
import json
import time
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

# ── 1. Check CUDA Availability ──
print("=" * 60)
print(f"  XGBoost CUDA Model Training")
print("=" * 60)

# ── 2. Load Dataset ──
data_path = "data/energy_consumption_mumbai_satara.csv"
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_dataset.py first.")

df = pd.read_csv(data_path)
print(f"Loaded dataset: {len(df):,} samples")

# Feature Engineering
df["temp_x_star"] = df["temperature_celsius"] * df["star_rating"]
df["temp_x_usage"] = df["temperature_celsius"] * df["usage_hours"]
df["star_x_usage"] = df["star_rating"] * df["usage_hours"]
df["temp_squared"] = df["temperature_celsius"] ** 2
df["humidity_x_temp"] = df["humidity_percent"] * df["temperature_celsius"] / 100.0

# One-hot encoding
df_encoded = pd.get_dummies(df, columns=["device_type", "city"])

# Target and features
target_col = "energy_consumption_kwh"
features = df_encoded.drop(columns=[target_col])
feature_names = features.columns.tolist()

X = features.values
y = df_encoded[target_col].values

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ── 3. Define Monotonic Constraints ──
# We want to force XGBoost to learn that as Temperature increases, Energy MUST increase.
# 1 = positive constraint, -1 = negative constraint, 0 = no constraint
constraints = []
for col in feature_names:
    if col == "temperature_celsius":
        constraints.append(1)  # Strictly positive correlation
    else:
        constraints.append(0)

# ── 4. Train Model with CUDA ──
print(f"\n Starting training using XGBoost on CUDA...")
start_time = time.time()

model = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=8,
    tree_method='hist',
    device='cuda',
    monotone_constraints=tuple(constraints),
    random_state=42
)

model.fit(X_train_scaled, y_train)

train_time = time.time() - start_time
print(f" Training completed in {train_time:.2f} seconds")

# ── 5. Evaluate Model ──
y_pred = model.predict(X_test_scaled)
y_true = y_test

r2 = r2_score(y_true, y_pred)
mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))

print("\n============================================================")
print(f"  XGBOOST CUDA MODEL RESULTS")
print("============================================================")
print(f"   R² Score:  {r2:.4f}")
print(f"   MAE:       {mae:.4f} kWh")
print(f"   RMSE:      {rmse:.4f} kWh")
print("============================================================")

# ── 6. Save Artifacts ──
os.makedirs("models", exist_ok=True)

# Save XGBoost Model using joblib to preserve scikit-learn wrapper
joblib.dump(model, "models/energy_predictor_cuda.pkl")

# Save Scaler
joblib.dump(scaler, "models/energy_scaler_cuda.pkl")

# Save Metrics and Metadata
metrics = {
    "ensemble_r2": float(r2),
    "ensemble_mae": float(mae),
    "ensemble_rmse": float(rmse),
    "feature_names": feature_names,
    "num_train_samples": len(X_train),
    "num_test_samples": len(X_test),
    "total_samples": len(df),
    "training_device": "cuda"
}

with open("models/model_metrics_cuda.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("\n Models saved to models/")
print("   - energy_predictor_cuda.pkl")
print("   - energy_scaler_cuda.pkl")
print("   - model_metrics_cuda.json")
