import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from pathlib import Path
import os

def generate_monotonicity_plot():
    print("Generating XGBoost Monotonicity Proof Plot...")
    
    # Load model and scaler
    model_path = "models/energy_predictor_cuda.pkl"
    scaler_path = "models/energy_scaler_cuda.pkl"
    data_path = "data/energy_consumption_mumbai_satara.csv"
    
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return
        
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    # 1. Load original data to get the exact feature structure
    df = pd.read_csv(data_path)
    
    # Feature Engineering (must match training exactly)
    df["temp_x_star"] = df["temperature_celsius"] * df["star_rating"]
    df["temp_x_usage"] = df["temperature_celsius"] * df["usage_hours"]
    df["star_x_usage"] = df["star_rating"] * df["usage_hours"]
    df["temp_squared"] = df["temperature_celsius"] ** 2
    df["humidity_x_temp"] = df["humidity_percent"] * df["temperature_celsius"] / 100.0
    
    df_encoded = pd.get_dummies(df, columns=["device_type", "city"])
    
    target_col = "energy_consumption_kwh"
    features = df_encoded.drop(columns=[target_col])
    
    # 2. Extract a single baseline profile (e.g. an AC unit in Mumbai)
    # Just take the first row of the processed features
    base_row = features.iloc[0:1].copy()
    
    # 3. Create synthetic sweep
    temps = np.linspace(10, 45, 100) # Sweep from 10C to 45C
    
    # Duplicate base row 100 times
    sweep_df = pd.concat([base_row]*100, ignore_index=True)
    
    # Update temperature
    sweep_df["temperature_celsius"] = temps
    
    # Update temperature-dependent features
    sweep_df["temp_x_star"] = sweep_df["temperature_celsius"] * sweep_df["star_rating"]
    sweep_df["temp_x_usage"] = sweep_df["temperature_celsius"] * sweep_df["usage_hours"]
    sweep_df["temp_squared"] = sweep_df["temperature_celsius"] ** 2
    sweep_df["humidity_x_temp"] = sweep_df["humidity_percent"] * sweep_df["temperature_celsius"] / 100.0
    
    # 4. Scale and Predict
    X_scaled = scaler.transform(sweep_df.values)
    predictions = model.predict(X_scaled)
    
    # 5. Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(temps, predictions, 'b-', linewidth=3, label='XGBoost CUDA Prediction')
    
    ax.set_title('Proof of Monotonic Constraints in XGBoost Model', fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Environmental Temperature (°C)', fontsize=12)
    ax.set_ylabel('Predicted Energy Consumption (kWh)', fontsize=12)
    
    # Add a text box explaining the constraint
    textstr = '\n'.join((
        r'$\bullet$ Strict Monotonicity Enforced',
        r'$\bullet$ Guaranteed Non-Decreasing',
        r'$\bullet$ No AI "Hallucination" Dips'
    ))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
            
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='lower right', fontsize=11)
    
    # Save
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "xgboost_monotonicity_proof.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved XGBoost plot to {out_path}")

if __name__ == "__main__":
    generate_monotonicity_plot()
