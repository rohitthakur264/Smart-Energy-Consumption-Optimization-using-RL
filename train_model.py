#!/usr/bin/env python3
"""
Train Multi-Modal Energy Consumption Prediction Model
Ensemble: Random Forest + Gradient Boosting Regressor
Target: R² > 95% on test set

Features: temperature, star_rating, device_type, city, humidity, usage_hours, month
Target: energy_consumption_kwh
"""
import os
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def load_and_prepare_data(csv_path):
    """Load dataset and prepare features."""
    print(f"Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"  Samples: {len(df):,}")
    print(f"  Columns: {list(df.columns)}")
    
    # ── Feature Engineering ──
    # One-hot encode device_type
    device_dummies = pd.get_dummies(df["device_type"], prefix="device")
    
    # One-hot encode city
    city_dummies = pd.get_dummies(df["city"], prefix="city")
    
    # Interaction features
    df["temp_x_star"] = df["temperature_celsius"] * df["star_rating"]
    df["temp_x_usage"] = df["temperature_celsius"] * df["usage_hours"]
    df["star_x_usage"] = df["star_rating"] * df["usage_hours"]
    df["temp_squared"] = df["temperature_celsius"] ** 2
    df["humidity_x_temp"] = df["humidity_percent"] * df["temperature_celsius"] / 100.0
    
    # Combine all features
    feature_cols = [
        "temperature_celsius", "humidity_percent", "star_rating", 
        "usage_hours", "month",
        "temp_x_star", "temp_x_usage", "star_x_usage", 
        "temp_squared", "humidity_x_temp"
    ]
    
    X = pd.concat([df[feature_cols], device_dummies, city_dummies], axis=1)
    y = df["energy_consumption_kwh"]
    
    # Save column order for inference
    feature_names = list(X.columns)
    
    return X, y, feature_names, df


def train_ensemble(X_train, y_train, X_test, y_test):
    """Train Random Forest + Gradient Boosting ensemble."""
    
    # ── Model 1: Random Forest ──
    print("\n🌲 Training Random Forest Regressor...")
    rf = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        n_jobs=-1,
        random_state=42,
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_r2 = r2_score(y_test, rf_pred)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    print(f"   R²:  {rf_r2:.4f}")
    print(f"   MAE: {rf_mae:.4f} kWh")
    
    # ── Model 2: Gradient Boosting ──
    print("\n🚀 Training Gradient Boosting Regressor...")
    gbr = GradientBoostingRegressor(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.8,
        random_state=42,
    )
    gbr.fit(X_train, y_train)
    gbr_pred = gbr.predict(X_test)
    gbr_r2 = r2_score(y_test, gbr_pred)
    gbr_mae = mean_absolute_error(y_test, gbr_pred)
    print(f"   R²:  {gbr_r2:.4f}")
    print(f"   MAE: {gbr_mae:.4f} kWh")
    
    # ── Ensemble: Weighted Average ──
    # Give more weight to the better model
    if rf_r2 >= gbr_r2:
        w_rf, w_gbr = 0.6, 0.4
    else:
        w_rf, w_gbr = 0.4, 0.6
    
    ensemble_pred = w_rf * rf_pred + w_gbr * gbr_pred
    ensemble_r2 = r2_score(y_test, ensemble_pred)
    ensemble_mae = mean_absolute_error(y_test, ensemble_pred)
    ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
    
    print(f"\n{'='*60}")
    print(f"  🏆 ENSEMBLE MODEL RESULTS (RF={w_rf}, GBR={w_gbr})")
    print(f"{'='*60}")
    print(f"   R² Score:  {ensemble_r2:.4f}  ({'✅ ABOVE 95%' if ensemble_r2 > 0.95 else '⚠️ BELOW 95%'})")
    print(f"   MAE:       {ensemble_mae:.4f} kWh")
    print(f"   RMSE:      {ensemble_rmse:.4f} kWh")
    print(f"{'='*60}")
    
    return rf, gbr, w_rf, w_gbr, {
        "rf_r2": round(rf_r2, 4),
        "gbr_r2": round(gbr_r2, 4),
        "ensemble_r2": round(ensemble_r2, 4),
        "ensemble_mae": round(ensemble_mae, 4),
        "ensemble_rmse": round(ensemble_rmse, 4),
        "rf_weight": w_rf,
        "gbr_weight": w_gbr,
    }


def compute_per_device_metrics(rf, gbr, w_rf, w_gbr, X_test, y_test, df_test):
    """Compute accuracy metrics per device type."""
    device_cols = [c for c in X_test.columns if c.startswith("device_")]
    per_device = {}
    
    for col in device_cols:
        device_name = col.replace("device_", "")
        mask = X_test[col] == 1
        if mask.sum() < 5:
            continue
        
        X_sub = X_test[mask]
        y_sub = y_test[mask]
        
        pred = w_rf * rf.predict(X_sub) + w_gbr * gbr.predict(X_sub)
        r2 = r2_score(y_sub, pred)
        mae = mean_absolute_error(y_sub, pred)
        
        per_device[device_name] = {
            "r2": round(r2, 4),
            "mae": round(mae, 4),
            "samples": int(mask.sum()),
        }
    
    return per_device


def main():
    print("=" * 70)
    print("  Multi-Modal Energy Consumption Model Training")
    print("  Ensemble: Random Forest + Gradient Boosting")
    print("=" * 70)
    
    # ── Load Data ──
    csv_path = Path("data/energy_consumption_mumbai_satara.csv")
    if not csv_path.exists():
        print(f"❌ Dataset not found at {csv_path}")
        print("   Run: python generate_dataset.py")
        return
    
    X, y, feature_names, df = load_and_prepare_data(csv_path)
    
    # ── Scale Features ──
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    
    # ── Split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    print(f"\n  Train: {len(X_train):,} | Test: {len(X_test):,}")
    
    # ── Train ──
    rf, gbr, w_rf, w_gbr, metrics = train_ensemble(X_train, y_train, X_test, y_test)
    
    # ── Per-device metrics ──
    df_test_original = df.iloc[X_test.index]
    per_device = compute_per_device_metrics(rf, gbr, w_rf, w_gbr, X_test, y_test, df_test_original)
    
    print("\n📊 Per-Device Accuracy:")
    for device, m in sorted(per_device.items()):
        status = "✅" if m["r2"] > 0.90 else "⚠️"
        print(f"   {status} {device:25s} R²={m['r2']:.4f}  MAE={m['mae']:.4f} kWh  (n={m['samples']})")
    
    # ── Save Models ──
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_bundle = {
        "rf": rf,
        "gbr": gbr,
        "rf_weight": w_rf,
        "gbr_weight": w_gbr,
        "feature_names": feature_names,
    }
    
    joblib.dump(model_bundle, models_dir / "energy_predictor.pkl")
    joblib.dump(scaler, models_dir / "energy_scaler.pkl")
    
    # Save metrics as JSON for the backend to serve
    all_metrics = {
        **metrics,
        "per_device": per_device,
        "feature_names": feature_names,
        "num_train_samples": len(X_train),
        "num_test_samples": len(X_test),
        "total_samples": len(df),
    }
    
    with open(models_dir / "model_metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=2)
    
    print(f"\n✅ Models saved to: {models_dir}/")
    print(f"   energy_predictor.pkl ({(models_dir / 'energy_predictor.pkl').stat().st_size / 1024:.0f} KB)")
    print(f"   energy_scaler.pkl")
    print(f"   model_metrics.json")
    print(f"\n🎯 Final Ensemble R²: {metrics['ensemble_r2']:.4f}")


if __name__ == "__main__":
    main()
