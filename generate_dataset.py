#!/usr/bin/env python3
"""
Generate Realistic Indian Appliance Energy Consumption Dataset
Cities: Mumbai (coastal, hot & humid) vs Satara (inland, moderate)
Features: temperature, star_rating, device_type, usage_hours, city, month, humidity
Target: energy_consumption_kwh
"""
import os
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# ── City Climate Profiles ──────────────────────────────────────────────
CITY_PROFILES = {
    "Mumbai": {
        # Monthly avg temps (Jan–Dec) based on IMD data
        "monthly_temp_mean": [25.4, 26.1, 28.2, 30.5, 32.1, 31.2, 29.5, 29.1, 29.3, 30.8, 29.2, 26.8],
        "monthly_temp_std":  [1.8,  1.9,  2.0,  1.8,  2.2,  1.6,  1.2,  1.1,  1.3,  1.7,  1.8,  1.9],
        # Monthly avg humidity (%)
        "monthly_humidity_mean": [62, 60, 63, 68, 72, 82, 88, 87, 84, 76, 68, 63],
        "monthly_humidity_std":  [6,  7,  7,  6,  7,  5,  4,  4,  5,  6,  7,  7],
        # Electricity rate (₹/kWh) — MSEDCL residential slab average
        "elec_rate": 8.50,
    },
    "Satara": {
        "monthly_temp_mean": [22.1, 23.8, 27.2, 30.1, 31.5, 27.8, 25.2, 24.8, 25.5, 27.3, 24.5, 22.0],
        "monthly_temp_std":  [2.5,  2.6,  2.8,  2.4,  2.8,  2.2,  1.6,  1.5,  1.8,  2.3,  2.5,  2.6],
        "monthly_humidity_mean": [48, 42, 38, 42, 52, 76, 84, 83, 78, 62, 52, 48],
        "monthly_humidity_std":  [8,  8,  9,  8,  9,  6,  5,  5,  6,  8,  8,  9],
        "elec_rate": 7.80,
    },
}

# ── Device Specifications (based on BEE/BIS standards) ──────────────────
# base_power_w: power at star_rating=3 (mid-range)
# star_factor: multiplier per star deviation from 3
#   star=1 → base * (1 + 2*star_factor), star=5 → base * (1 - 2*star_factor)
# temp_sensitivity: how much temperature affects energy (0=none, 1=high)
#   ALL devices: higher temperature → higher energy consumption
DEVICES = {
    "Air Conditioner": {
        "base_power_w": 1500,
        "star_factor": 0.12,
        "temp_sensitivity": 0.95,
        "usage_range": (2, 12),
    },
    "Refrigerator": {
        "base_power_w": 150,
        "star_factor": 0.15,
        "temp_sensitivity": 0.50,
        "usage_range": (20, 24),
    },
    "Ceiling Fan": {
        "base_power_w": 70,
        "star_factor": 0.18,
        "temp_sensitivity": 0.65,
        "usage_range": (4, 16),
    },
    "LED TV": {
        "base_power_w": 80,
        "star_factor": 0.10,
        "temp_sensitivity": 0.15,
        "usage_range": (2, 8),
    },
    "Washing Machine": {
        "base_power_w": 500,
        "star_factor": 0.14,
        "temp_sensitivity": 0.20,
        "usage_range": (0.5, 2),
    },
    "Water Heater (Geyser)": {
        "base_power_w": 2000,
        "star_factor": 0.10,
        "temp_sensitivity": 0.40,
        "usage_range": (0.5, 3),
    },
    "Room Heater": {
        "base_power_w": 1800,
        "star_factor": 0.08,
        "temp_sensitivity": 0.35,
        "usage_range": (1, 6),
    },
    "Microwave Oven": {
        "base_power_w": 1200,
        "star_factor": 0.08,
        "temp_sensitivity": 0.18,
        "usage_range": (0.3, 1.5),
    },
    "Desktop Computer": {
        "base_power_w": 250,
        "star_factor": 0.12,
        "temp_sensitivity": 0.20,
        "usage_range": (2, 10),
    },
    "Iron": {
        "base_power_w": 1000,
        "star_factor": 0.06,
        "temp_sensitivity": 0.12,
        "usage_range": (0.3, 1.5),
    },
}


def compute_energy(device_name, device_spec, temperature, humidity, star_rating, usage_hours):
    """
    Compute energy consumption (kWh) for a device given environmental conditions.
    
    KEY RULE: Higher temperature → Higher energy consumption for ALL devices.
    - Hot weather increases cooling load for AC, Fridge, Fan
    - Hot weather increases thermal stress on electronics (need more cooling)
    - Hot weather increases power draw for all motors and compressors
    - Geyser/Heater need more power to overcome ambient heat transfer losses
    """
    base_power = device_spec["base_power_w"]
    
    # Star rating efficiency: lower star = more power consumption
    # Star 1 = +24% power, Star 2 = +12%, Star 3 = baseline, Star 4 = -12%, Star 5 = -24%
    star_multiplier = 1.0 + (3 - star_rating) * device_spec["star_factor"]
    
    # ── TEMPERATURE IMPACT: ALWAYS POSITIVE CORRELATION ──
    # All devices consume MORE energy when temperature is HIGHER
    # Normalized: at 10°C = baseline (1.0), each degree above adds energy
    temp_sens = device_spec["temp_sensitivity"]
    temp_delta = max(0, temperature - 10.0)  # baseline at 10°C
    temp_multiplier = 1.0 + temp_sens * (temp_delta / 30.0)
    
    # Humidity impact (higher humidity → more energy for all devices)
    humidity_factor = 1.0 + 0.08 * ((humidity - 50) / 50.0)
    
    # Final power (W) with all multipliers
    effective_power = base_power * star_multiplier * temp_multiplier * humidity_factor
    
    # Energy = Power × Time (convert W to kW)
    energy_kwh = (effective_power / 1000.0) * usage_hours
    
    # Add very small random noise (±1%) to keep ML curves smooth and strictly monotonic
    noise = np.random.normal(1.0, 0.01)
    energy_kwh *= max(0.01, noise)
    
    return round(energy_kwh, 4)


def generate_dataset(num_samples=10000):
    """Generate the full dataset."""
    records = []
    
    cities = list(CITY_PROFILES.keys())
    device_names = list(DEVICES.keys())
    star_ratings = [1, 2, 3, 4, 5]
    months = list(range(1, 13))
    
    samples_per_combo = max(1, num_samples // (len(cities) * len(device_names) * len(star_ratings) * len(months)))
    
    for city in cities:
        profile = CITY_PROFILES[city]
        for month in months:
            m_idx = month - 1
            for device_name in device_names:
                spec = DEVICES[device_name]
                for star in star_ratings:
                    for _ in range(samples_per_combo):
                        # Sample temperature from city+month distribution
                        temp = np.random.normal(
                            profile["monthly_temp_mean"][m_idx],
                            profile["monthly_temp_std"][m_idx]
                        )
                        temp = round(np.clip(temp, 8.0, 48.0), 1)
                        
                        # Sample humidity
                        humidity = np.random.normal(
                            profile["monthly_humidity_mean"][m_idx],
                            profile["monthly_humidity_std"][m_idx]
                        )
                        humidity = round(np.clip(humidity, 15.0, 98.0), 1)
                        
                        # Sample usage hours
                        low, high = spec["usage_range"]
                        usage = round(np.random.uniform(low, high), 1)
                        
                        # Higher temperature → slightly more usage hours for all devices
                        if temp > 35:
                            usage = round(min(usage * 1.2, spec["usage_range"][1]), 1)
                        
                        # 30% of the time, inject purely uniform samples across the absolute bounds.
                        # This prevents the ML tree models (RF/GBR) from hallucinating/extrapolating 
                        # poorly when the user selects edge-case combinations in the UI 
                        # (e.g., an AC running for only 0.5 hours at 48°C).
                        if np.random.rand() < 0.30:
                            temp = round(np.random.uniform(10.0, 48.0), 1)
                            humidity = round(np.random.uniform(15.0, 95.0), 1)
                            usage = round(np.random.uniform(0.5, 24.0), 1)
                        
                        # Compute energy
                        energy = compute_energy(device_name, spec, temp, humidity, star, usage)
                        
                        records.append({
                            "city": city,
                            "month": month,
                            "temperature_celsius": temp,
                            "humidity_percent": humidity,
                            "device_type": device_name,
                            "star_rating": star,
                            "usage_hours": usage,
                            "energy_consumption_kwh": energy,
                        })
    
    df = pd.DataFrame(records)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
    
    return df


def main():
    print("=" * 70)
    print("  Generating Indian Appliance Energy Consumption Dataset")
    print("  Cities: Mumbai (coastal) vs Satara (inland)")
    print("=" * 70)
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate
    df = generate_dataset(num_samples=12000)
    
    # Save
    out_path = data_dir / "energy_consumption_mumbai_satara.csv"
    df.to_csv(out_path, index=False)
    
    # Stats
    print(f"\n✅ Dataset saved to: {out_path}")
    print(f"   Total samples: {len(df):,}")
    print(f"\n📊 Summary by City:")
    city_stats = df.groupby("city")["energy_consumption_kwh"].agg(["mean", "std", "count"])
    print(city_stats.to_string())
    
    print(f"\n📊 Summary by Device:")
    device_stats = df.groupby("device_type")["energy_consumption_kwh"].agg(["mean", "std", "count"])
    print(device_stats.to_string())
    
    print(f"\n📊 Summary by Star Rating:")
    star_stats = df.groupby("star_rating")["energy_consumption_kwh"].agg(["mean", "std"])
    print(star_stats.to_string())
    
    print(f"\n📊 Mumbai vs Satara Average Energy (kWh):")
    comparison = df.groupby(["city", "device_type"])["energy_consumption_kwh"].mean().unstack(0)
    print(comparison.to_string())
    
    print(f"\n✅ Dataset generation complete!")
    return df


if __name__ == "__main__":
    main()
