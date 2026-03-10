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
        # Ensure data exists
        if not os.path.exists(DATA_PATH):
            print(f"Warning: {DATA_PATH} not found. Creating dummy placeholder.")
            # Create a dummy file so RLController can initialize
            # The user will overwrite this via upload or generation endpoints
            with open(DATA_PATH, 'w') as f:
                f.write("dummy,header\n0,0")
        
        # Find models
        model_paths = {}
        if os.path.exists(MODEL_DIR):
            for f in os.listdir(MODEL_DIR):
                if f.endswith(".zip"):
                    # Clean name: ppo_enhanced_ppo_final.zip -> enhanced
                    name = f.replace(".zip", "").replace("ppo_", "").replace("_final", "").replace("_agent", "")
                    model_paths[name] = os.path.join(MODEL_DIR, f)
                    # Also keep original name just in case
                    model_paths[f.replace(".zip", "")] = os.path.join(MODEL_DIR, f)
        
        controller = RLController(DATA_PATH, model_paths)
    return controller

@router.get("/status")
async def get_status():
    try:
        c = get_controller()
        return c.get_status()
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.get("/simulate")
async def run_simulation(num_days: int = 5, use_model: bool = False, model_name: str = "enhanced"):
    c = get_controller()
    return c.run_simulation(num_days, use_model, model_name)

@router.get("/evaluate")
async def evaluate_model(model_name: str = "enhanced", num_episodes: int = 5):
    c = get_controller()
    return c.run_evaluation(model_name, num_episodes)

@router.get("/compare")
async def compare_models(num_days: int = 3):
    c = get_controller()
    # Run baseline
    baseline = c.run_simulation(num_days, use_model=False)
    # Run enhanced
    enhanced = c.run_simulation(num_days, use_model=True, model_name="enhanced")
    
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
    c = get_controller()
    new_path = c.generate_synthetic_dataset(num_buildings)
    return {"message": f"Generated {num_buildings} buildings", "path": new_path}

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