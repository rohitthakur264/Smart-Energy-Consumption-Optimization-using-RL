"""
Simulation Routes — Real-time simulation API endpoints.
"""
from fastapi import APIRouter, Query, UploadFile, File, HTTPException
import shutil
from backend.services.rl_controller import RLController
import os

router = APIRouter(prefix="/api", tags=["simulation"])

# Resolve data and model paths relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, "energy_data_cleaned.csv")
MODEL_PATHS = {
    "enhanced": os.path.join(PROJECT_ROOT, "models", "ppo_enhanced_ppo_final.zip"),
    "hvac": os.path.join(PROJECT_ROOT, "models", "ppo_multi_agent_hvac_agent.zip"),
    "lighting": os.path.join(PROJECT_ROOT, "models", "ppo_multi_agent_lighting_agent.zip"),
}

# Initialize controller (models loaded once at startup)
controller = RLController(DATA_PATH, model_paths=MODEL_PATHS)


@router.get("/simulate")
def simulate(
    num_days: int = Query(default=5, ge=1, le=30, description="Number of days to simulate"),
    use_model: bool = Query(default=False, description="Use trained RL model vs baseline"),
    model_name: str = Query(default="enhanced", description="Which model to use"),
    peak_rate: float = Query(default=5.0),
    mid_rate: float = Query(default=3.5),
    off_peak_rate: float = Query(default=2.0)
):
    """
    Run building energy simulation.
    Returns hourly data and aggregate metrics for real-time dashboard.
    """
    result = controller.run_simulation(
        num_days=num_days,
        use_model=use_model,
        model_name=model_name,
        peak_rate=peak_rate,
        mid_rate=mid_rate,
        off_peak_rate=off_peak_rate
    )
    return result


@router.get("/evaluate")
def evaluate(
    model_name: str = Query(default="enhanced", description="Model to evaluate"),
    num_episodes: int = Query(default=5, ge=1, le=50, description="Evaluation episodes"),
):
    """
    Run multi-episode evaluation of a trained model.
    Returns per-episode metrics and summary statistics.
    """
    result = controller.run_evaluation(
        model_name=model_name,
        num_episodes=num_episodes,
    )
    return result


@router.get("/status")
def status():
    """Health check and system info."""
    return controller.get_status()

@router.post("/generate-dataset")
def generate_dataset(num_buildings: int = Query(default=50)):
    """Generate a synthetic CSV dataset and switch to using it."""
    try:
        path = controller.generate_synthetic_dataset(num_buildings)
        return {"status": "success", "message": f"Generated synthetic dataset with {num_buildings} buildings", "file": path}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a custom CSV dataset and switch to using it for simulations."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
    try:
        # Save the uploaded file
        upload_dir = os.path.join(PROJECT_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update controller to use the new data path
        controller.data_path = file_path
        
        return {
            "status": "success", 
            "message": f"Successfully uploaded and loaded {file.filename}",
            "file": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.get("/compare")
def compare(
    num_days: int = Query(default=3, ge=1, le=10, description="Number of days"),
):
    """
    Compare RL model vs baseline side by side.
    """
    baseline = controller.run_simulation(num_days=num_days, use_model=False)
    rl_result = controller.run_simulation(num_days=num_days, use_model=True, model_name="enhanced")
    
    return {
        "baseline": baseline,
        "rl_optimized": rl_result,
        "savings": {
            "energy_saved_kwh": round(baseline['metrics']['total_energy'] - rl_result['metrics']['total_energy'], 2),
            "cost_saved": round(baseline['metrics']['total_cost'] - rl_result['metrics']['total_cost'], 2),
            "comfort_improvement": round(rl_result['metrics']['comfort_score'] - baseline['metrics']['comfort_score'], 1),
        }
    }
