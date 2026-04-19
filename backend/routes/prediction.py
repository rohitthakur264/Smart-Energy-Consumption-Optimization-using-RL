"""
Energy Prediction API Routes
Endpoints for multi-modal energy consumption prediction (Mumbai vs Satara).
"""
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["Energy Prediction"])

# Lazy-loaded service instance
_service = None

def get_service():
    global _service
    if _service is None:
        from backend.services.prediction_service import EnergyPredictionService
        print("Initializing EnergyPredictionService...")
        _service = EnergyPredictionService()
        print("[OK] EnergyPredictionService ready.")
    return _service


@router.get("/predict")
async def predict_energy(
    temperature: float = Query(30.0, description="Temperature in Celsius"),
    star_rating: int = Query(3, ge=1, le=5, description="BEE Star Rating (1-5)"),
    device_type: str = Query("Air Conditioner", description="Device type"),
    city: str = Query("Mumbai", description="City (Mumbai or Satara)"),
    humidity: float = Query(65.0, description="Humidity percentage"),
    usage_hours: float = Query(4.0, description="Daily usage hours"),
    month: int = Query(6, ge=1, le=12, description="Month (1-12)"),
):
    """Predict energy consumption for a device given environmental conditions."""
    try:
        svc = get_service()
        return svc.predict(temperature, star_rating, device_type, city, humidity, usage_hours, month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/compare-cities")
async def compare_cities():
    """Compare Mumbai vs Satara energy consumption across all devices."""
    try:
        svc = get_service()
        return svc.compare_cities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/model-metrics")
async def get_model_metrics():
    """Return trained model accuracy metrics (R2, MAE, RMSE)."""
    try:
        svc = get_service()
        return svc.get_model_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.get("/temperature-impact")
async def get_temperature_impact(
    device_type: str = Query("Air Conditioner"),
    city: str = Query("Mumbai"),
):
    """Get energy vs temperature curve for different star ratings."""
    try:
        svc = get_service()
        return svc.get_temperature_impact(device_type, city)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.get("/star-impact")
async def get_star_impact(
    device_type: str = Query("Air Conditioner"),
):
    """Get energy vs star rating for a device across both cities."""
    try:
        svc = get_service()
        return svc.get_star_impact(device_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.get("/available-devices")
async def get_available_devices():
    """Return list of available device types."""
    try:
        svc = get_service()
        return {"devices": svc.get_available_devices()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
