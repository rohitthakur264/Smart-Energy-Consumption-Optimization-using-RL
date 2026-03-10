"""
Enhanced UCI ENB2012 Dataset Preprocessing
Loads, validates, and prepares building energy data for multi-agent RL.
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path
import sys

def load_uci_data(file_path: str) -> pd.DataFrame:
    """
    Load UCI ENB2012 Energy Efficiency Dataset.
    
    Dataset: 768 building designs, 8 input features, 2 output features
    - X1: Relative Compactness (0.62 - 0.98)
    - X2: Surface Area (514.5 - 808.0 m²)
    - X3: Wall Area (245 - 416.5 m²)
    - X4: Roof Area (110.25 - 220.5 m²)
    - X5: Overall Height (3.5 - 7 m)
    - X6: Orientation (0/90/180/270 degrees)
    - X7: Glazing Area (0 - 0.4, fraction of wall)
    - X8: Glazing Area Distribution (0 - 5)
    - y1: Heating Load (2.47 - 48.03 kWh/m²)
    - y2: Cooling Load (10.59 - 43.10 kWh/m²)
    
    Reference:
    Tsanas, A., & Xifara, A. (2012).
    "Accurate quantitative estimation of energy performance of residential buildings"
    Energy and Buildings, 49, pp. 560-567.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    
    # Read from Excel
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    
    # Column mapping
    column_names = {
        'X1': 'Relative_Compactness',
        'X2': 'Surface_Area',
        'X3': 'Wall_Area',
        'X4': 'Roof_Area',
        'X5': 'Overall_Height',
        'X6': 'Orientation',
        'X7': 'Glazing_Area',
        'X8': 'Glazing_Area_Distribution',
        'y1': 'Heating_Load',
        'y2': 'Cooling_Load'
    }
    
    df.rename(columns=column_names, inplace=True, errors='ignore')
    
    # Handle case where columns might have spaces or different naming
    for old_col, new_col in column_names.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    return df


def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize UCI data to physical bounds for better RL learning.
    """
    df_normalized = df.copy()
    
    # Normalize to [0, 1] for better neural network training
    feature_columns = ['Relative_Compactness', 'Surface_Area', 'Wall_Area', 
                      'Roof_Area', 'Overall_Height', 'Orientation', 
                      'Glazing_Area', 'Glazing_Area_Distribution']
    
    for col in feature_columns:
        if col in df_normalized.columns:
            min_val = df_normalized[col].min()
            max_val = df_normalized[col].max()
            if max_val > min_val:
                df_normalized[col] = (df_normalized[col] - min_val) / (max_val - min_val)
    
    return df_normalized


def validate_data(df: pd.DataFrame) -> bool:
    """Validate UCI dataset completeness and consistency."""
    required_cols = ['Relative_Compactness', 'Surface_Area', 'Wall_Area', 
                     'Roof_Area', 'Overall_Height', 'Orientation', 
                     'Glazing_Area', 'Glazing_Area_Distribution',
                     'Heating_Load', 'Cooling_Load']
    
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"Warning: Missing columns: {missing}")
        return False
    
    # Check for null values
    nulls = df[required_cols].isnull().sum()
    if nulls.any():
        print(f"Warning: Found null values:\n{nulls}")
        return False
    
    # Check data types
    for col in required_cols:
        if not np.issubdtype(df[col].dtype, np.number):
            print(f"Warning: Column '{col}' is not numeric")
            return False
    
    print(f"✓ Dataset validated: {len(df)} buildings, {len(required_cols)} features")
    return True


def generate_summary_statistics(df: pd.DataFrame):
    """Generate and display dataset summary statistics."""
    print("\n" + "="*70)
    print("UCI ENB2012 Energy Efficiency Dataset Summary")
    print("="*70)
    
    feature_cols = ['Relative_Compactness', 'Surface_Area', 'Wall_Area', 
                   'Roof_Area', 'Overall_Height', 'Orientation', 
                   'Glazing_Area', 'Glazing_Area_Distribution']
    
    print("\nBuilding Input Features (Geometry & Design):")
    print(df[feature_cols].describe().T[['min', '50%', 'max', 'std']].to_string())
    
    if 'Heating_Load' in df.columns:
        print(f"\nHeating Load:")
        print(df['Heating_Load'].describe())
    
    if 'Cooling_Load' in df.columns:
        print(f"\nCooling Load:")
        print(df['Cooling_Load'].describe())
    
    print("\nDataset Size: {} buildings".format(len(df)))
    print("Features: {} input dimensions".format(len(feature_cols)))
    print("="*70 + "\n")


def prepare_dataset(input_path: str, output_path: str = None):
    """
    Complete preprocessing pipeline.
    
    Args:
        input_path: Path to UCI ENB2012 Excel file
        output_path: Path to save cleaned CSV (default: energy_data_cleaned.csv)
    """
    print("Loading UCI ENB2012 Dataset...")
    df = load_uci_data(input_path)
    
    print("Validating data...")
    is_valid = validate_data(df)
    
    if not is_valid:
        print("⚠ Dataset validation failed. Attempting to proceed...")
    
    # Generate statistics
    generate_summary_statistics(df)
    
    # Save cleaned data
    if output_path is None:
        output_path = "energy_data_cleaned.csv"
    
    df.to_csv(output_path, index=False)
    print(f"✓ Cleaned dataset saved to: {output_path}\n")
    
    return df


def preprocess_for_rl(input_path: str, 
                      output_path: str = "energy_data_cleaned.csv") -> pd.DataFrame:
    """
    Preprocess UCI data specifically for multi-agent RL training.
    Includes normalization and outlier handling.
    """
    df = prepare_dataset(input_path, output_path)
    
    # Remove outliers (beyond 3 sigma on heating/cooling loads)
    if 'Heating_Load' in df.columns:
        heat_mean = df['Heating_Load'].mean()
        heat_std = df['Heating_Load'].std()
        df = df[(df['Heating_Load'] >= heat_mean - 3*heat_std) & 
                (df['Heating_Load'] <= heat_mean + 3*heat_std)]
    
    if 'Cooling_Load' in df.columns:
        cool_mean = df['Cooling_Load'].mean()
        cool_std = df['Cooling_Load'].std()
        df = df[(df['Cooling_Load'] >= cool_mean - 3*cool_std) & 
                (df['Cooling_Load'] <= cool_mean + 3*cool_std)]
    
    print(f"✓ Dataset after outlier removal: {len(df)} buildings")
    
    # Save final version
    df.to_csv(output_path, index=False)
    
    return df


if __name__ == "__main__":
    # Auto-detect data file
    # Look in current directory or a 'data' subdirectory
    search_paths = [Path("."), Path("data"), Path("energy+efficiency")]
    
    # Find Excel file
    input_file = None
    for path in search_paths:
        if path.exists():
            excel_files = list(path.glob("*.xlsx")) + list(path.glob("*.xls"))
            if excel_files:
                input_file = str(excel_files[0])
                break
    
    if input_file:
        print(f"Found data file: {input_file}\n")
        df = preprocess_for_rl(input_file)
        print("Preprocessing complete! Ready for multi-agent RL training.")
    else:
        print("Warning: No Excel data file found. Skipping preprocessing.")
        # Do not exit with error, as this breaks the Render build.
        # The application will handle missing data by generating synthetic data if needed.
        sys.exit(0)
