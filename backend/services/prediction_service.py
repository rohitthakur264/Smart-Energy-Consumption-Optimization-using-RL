"""
Energy Prediction Service — Multi-Modal Model
Loads trained ensemble (Random Forest + Gradient Boosting) for energy prediction.
"""
import os
import json
import os
import json
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class EnergyPredictionService:
    """Service to predict energy consumption using the trained ensemble model."""

    def __init__(self):
        self.model_bundle = None
        self.scaler = None
        self.metrics = None
        self.dataset = None
        self._load_model()
        self._load_dataset()

    def _load_model(self):
        """Load trained XGBoost CUDA model, scaler, and metrics."""
        models_dir = Path(PROJECT_ROOT) / "models"

        model_path = models_dir / "energy_predictor_cuda.pkl"
        scaler_path = models_dir / "energy_scaler_cuda.pkl"
        metrics_path = models_dir / "model_metrics_cuda.json"

        # Load metrics first to get input_dim
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                self.metrics = json.load(f)
            print(f"  [OK] Loaded model metrics (R2={self.metrics.get('ensemble_r2', 'N/A')})")

        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            print(f"  [OK] Loaded scaler")

        if model_path.exists() and self.metrics:
            self.model_bundle = joblib.load(model_path)
            print(f"  [OK] Loaded XGBoost energy predictor model (CUDA accelerated)")
        else:
            print(f"  [WARN] Model not found at {model_path}. Run train_model_cuda.py first.")

    def _load_dataset(self):
        """Load the dataset for statistical queries."""
        data_path = Path(PROJECT_ROOT) / "data" / "energy_consumption_mumbai_satara.csv"
        if data_path.exists():
            self.dataset = pd.read_csv(data_path)
            print(f"  [OK] Loaded dataset ({len(self.dataset):,} rows)")
        else:
            print(f"  [WARN] Dataset not found at {data_path}")

    def _build_feature_vector(self, temperature, humidity, star_rating, usage_hours, month, device_type, city):
        """Build a feature vector matching the training format."""
        if self.model_bundle is None:
            raise ValueError("Model not loaded. Run train_model.py first.")

        feature_names = self.metrics["feature_names"]

        # Create base features
        features = {
            "temperature_celsius": temperature,
            "humidity_percent": humidity,
            "star_rating": star_rating,
            "usage_hours": usage_hours,
            "month": month,
            "temp_x_star": temperature * star_rating,
            "temp_x_usage": temperature * usage_hours,
            "star_x_usage": star_rating * usage_hours,
            "temp_squared": temperature ** 2,
            "humidity_x_temp": humidity * temperature / 100.0,
        }

        # Add one-hot device columns
        device_columns = [c for c in feature_names if c.startswith("device_")]
        for col in device_columns:
            features[col] = 1.0 if col == f"device_{device_type}" else 0.0

        # Add one-hot city columns
        city_columns = [c for c in feature_names if c.startswith("city_")]
        for col in city_columns:
            features[col] = 1.0 if col == f"city_{city}" else 0.0

        # Build DataFrame with correct column order
        row = pd.DataFrame([features])[feature_names]
        return row

    def predict(self, temperature, star_rating, device_type, city, 
                humidity=65.0, usage_hours=4.0, month=6):
        """Predict energy consumption for given parameters."""
        if self.model_bundle is None:
            return {"error": "Model not loaded"}

        row = self._build_feature_vector(
            temperature, humidity, star_rating, usage_hours, month, device_type, city
        )

        # Scale (returns numpy array)
        row_scaled_array = self.scaler.transform(row)

        # XGBoost prediction
        pred = self.model_bundle.predict(row_scaled_array)[0]

        return {
            "energy_consumption_kwh": round(max(0.0, float(pred)), 4),
            "device_type": device_type,
            "city": city,
            "temperature": temperature,
            "star_rating": star_rating,
            "usage_hours": usage_hours,
            "humidity": humidity,
            "month": month,
        }

    def compare_cities(self):
        """Compare Mumbai vs Satara energy consumption across all devices and star ratings."""
        if self.dataset is None:
            return {"error": "Dataset not loaded"}

        devices = sorted(self.dataset["device_type"].unique().tolist())
        star_ratings = sorted(self.dataset["star_rating"].unique().tolist())

        # Per-device comparison (averaged across all star ratings)
        device_comparison = []
        for device in devices:
            mumbai_avg = float(self.dataset[
                (self.dataset["device_type"] == device) & (self.dataset["city"] == "Mumbai")
            ]["energy_consumption_kwh"].mean())

            satara_avg = float(self.dataset[
                (self.dataset["device_type"] == device) & (self.dataset["city"] == "Satara")
            ]["energy_consumption_kwh"].mean())

            device_comparison.append({
                "device": device,
                "mumbai_kwh": round(mumbai_avg, 3),
                "satara_kwh": round(satara_avg, 3),
                "difference_kwh": round(mumbai_avg - satara_avg, 3),
                "difference_pct": round(((mumbai_avg - satara_avg) / max(satara_avg, 0.001)) * 100, 1),
            })

        # Per-star-rating comparison
        star_comparison = []
        for star in star_ratings:
            mumbai_avg = float(self.dataset[
                (self.dataset["star_rating"] == star) & (self.dataset["city"] == "Mumbai")
            ]["energy_consumption_kwh"].mean())

            satara_avg = float(self.dataset[
                (self.dataset["star_rating"] == star) & (self.dataset["city"] == "Satara")
            ]["energy_consumption_kwh"].mean())

            star_comparison.append({
                "star_rating": star,
                "mumbai_kwh": round(mumbai_avg, 3),
                "satara_kwh": round(satara_avg, 3),
            })

        # City-level summaries
        mumbai_stats = self.dataset[self.dataset["city"] == "Mumbai"]
        satara_stats = self.dataset[self.dataset["city"] == "Satara"]

        return {
            "device_comparison": device_comparison,
            "star_comparison": star_comparison,
            "mumbai_summary": {
                "avg_energy_kwh": round(float(mumbai_stats["energy_consumption_kwh"].mean()), 3),
                "total_samples": len(mumbai_stats),
                "avg_temperature": round(float(mumbai_stats["temperature_celsius"].mean()), 1),
                "avg_humidity": round(float(mumbai_stats["humidity_percent"].mean()), 1),
            },
            "satara_summary": {
                "avg_energy_kwh": round(float(satara_stats["energy_consumption_kwh"].mean()), 3),
                "total_samples": len(satara_stats),
                "avg_temperature": round(float(satara_stats["temperature_celsius"].mean()), 1),
                "avg_humidity": round(float(satara_stats["humidity_percent"].mean()), 1),
            },
            "devices": devices,
            "star_ratings": star_ratings,
        }

    def get_temperature_impact(self, device_type="Air Conditioner", city="Mumbai"):
        """Get energy vs temperature curve for a device in a city."""
        if self.model_bundle is None:
            return {"error": "Model not loaded"}

        temps = list(range(15, 46))
        results = {"temperatures": temps, "star_1": [], "star_3": [], "star_5": []}

        for star in [1, 3, 5]:
            energies = []
            for temp in temps:
                pred = self.predict(
                    temperature=temp, star_rating=star, device_type=device_type,
                    city=city, humidity=70.0, usage_hours=4.0, month=6
                )
                energies.append(pred["energy_consumption_kwh"])
            results[f"star_{star}"] = energies

        results["device_type"] = device_type
        results["city"] = city
        return results

    def get_star_impact(self, device_type="Air Conditioner"):
        """Get energy vs star rating for a device across both cities."""
        if self.dataset is None:
            return {"error": "Dataset not loaded"}

        star_ratings = [1, 2, 3, 4, 5]
        mumbai_vals = []
        satara_vals = []

        for star in star_ratings:
            m = float(self.dataset[
                (self.dataset["device_type"] == device_type) &
                (self.dataset["star_rating"] == star) &
                (self.dataset["city"] == "Mumbai")
            ]["energy_consumption_kwh"].mean())
            mumbai_vals.append(round(m, 3))

            s = float(self.dataset[
                (self.dataset["device_type"] == device_type) &
                (self.dataset["star_rating"] == star) &
                (self.dataset["city"] == "Satara")
            ]["energy_consumption_kwh"].mean())
            satara_vals.append(round(s, 3))

        return {
            "star_ratings": star_ratings,
            "mumbai_kwh": mumbai_vals,
            "satara_kwh": satara_vals,
            "device_type": device_type,
        }

    def get_model_metrics(self):
        """Return model accuracy metrics."""
        if self.metrics is None:
            return {
                "error": "Metrics not available. Run train_model.py first.",
                "ensemble_r2": 0,
                "ensemble_mae": 0,
                "ensemble_rmse": 0,
            }
        return self.metrics

    def get_available_devices(self):
        """Return list of available device types."""
        if self.dataset is not None:
            return sorted(self.dataset["device_type"].unique().tolist())
        return [
            "Air Conditioner", "Ceiling Fan", "Desktop Computer",
            "Iron", "LED TV", "Microwave Oven", "Refrigerator",
            "Room Heater", "Washing Machine", "Water Heater (Geyser)"
        ]
