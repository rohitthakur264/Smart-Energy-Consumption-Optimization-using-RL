from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.rl_controller import RLController
import os
import shutil

router = APIRouter(prefix="/api", tags=["Simulation"])

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "energy_data_cleaned.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Global controller instance
controller = None

def get_controller():
    global controller
    if controller is None:
        try:
            # Ensure data exists
            if not os.path.exists(DATA_PATH):
                print(f"Warning: {DATA_PATH} not found. Creating dummy placeholder.")
                import pandas as pd
                import numpy as np
                dummy = pd.DataFrame({
                    col: np.random.uniform(0.6, 1.0, 20) for col in [
                        'Relative_Compactness','Surface_Area','Wall_Area',
                        'Roof_Area','Overall_Height','Orientation',
                        'Glazing_Area','Glazing_Area_Distribution',
                        'Heating_Load','Cooling_Load'
                    ]
                })
                dummy.to_csv(DATA_PATH, index=False)

            # Discover models and build name→path mapping
            model_paths = {}
            if os.path.exists(MODEL_DIR):
                for fname in os.listdir(MODEL_DIR):
                    if not fname.endswith(".zip"):
                        continue
                    full_path = os.path.join(MODEL_DIR, fname)
                    raw_name = fname[:-4]   # strip .zip

                    # Always register the raw file stem
                    model_paths[raw_name] = full_path

                    # Build a short alias: strip well-known prefixes/suffixes
                    alias = raw_name
                    for strip in ("ppo_", "a2c_", "_final", "_agent",
                                  "multi_agent_", "enhanced_ppo", "enhanced_a2c"):
                        alias = alias.replace(strip, "")
                    alias = alias.strip("_")

                    # Specific canonical aliases
                    if "enhanced" in raw_name and "multi" not in raw_name:
                        model_paths["enhanced"] = full_path
                    if "hvac" in raw_name:
                        model_paths["hvac"] = full_path
                    if "lighting" in raw_name:
                        model_paths["lighting"] = full_path

                    if alias and alias not in model_paths:
                        model_paths[alias] = full_path

                print(f"  Discovered models: {list(model_paths.keys())}")

            print("Initializing RLController...")
            controller = RLController(DATA_PATH, model_paths)
            print("✓ RLController initialized successfully.")

        except Exception as e:
            print(f"FATAL: Failed to initialize RLController: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service Unavailable: Could not initialize the simulation controller. Error: {e}"
            )
    return controller

@router.get("/status")
async def get_status():
    try:
        c = get_controller()
        return c.get_status()
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.get("/simulate")
async def run_simulation(
    num_days: int = 5,
    use_model: bool = False,
    model_name: str = "enhanced",
    peak_rate: float = 6.50,
    mid_rate: float = 4.50,
    off_peak_rate: float = 3.50,
):
    try:
        c = get_controller()
        return c.run_simulation(num_days, use_model, model_name,
                                peak_rate=peak_rate,
                                mid_rate=mid_rate,
                                off_peak_rate=off_peak_rate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.get("/evaluate")
async def evaluate_model(model_name: str = "enhanced", num_episodes: int = 5):
    try:
        c = get_controller()
        return c.run_evaluation(model_name, num_episodes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.get("/compare")
async def compare_models(num_days: int = 3):
    try:
        c = get_controller()
        # Run baseline
        baseline = c.run_simulation(num_days, use_model=False)
        # Run enhanced
        enhanced = c.run_simulation(num_days, use_model=True, model_name="enhanced")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
    
    return {
        "baseline": baseline['metrics'],
        "enhanced": enhanced['metrics'],
        "improvement": {
            "energy": baseline['metrics']['total_energy'] - enhanced['metrics']['total_energy'],
            "cost": baseline['metrics']['total_cost'] - enhanced['metrics']['total_cost']
        }
    }

@router.post("/generate-dataset")
async def generate_dataset(num_buildings: int = 50):
    try:
        c = get_controller()
        new_path = c.generate_synthetic_dataset(num_buildings)
        return {"message": f"Generated {num_buildings} buildings", "path": new_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset generation failed: {str(e)}")

@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(BASE_DIR, "energy_data_cleaned.csv")
        # Use async read/write to prevent blocking the server
        with open(file_location, "wb+") as file_object:
            content = await file.read()
            file_object.write(content)
        
        # Reload controller with new data
        global controller
        controller = None 
        get_controller()
        
        return {"message": "Dataset uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))