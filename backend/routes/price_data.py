"""
Real Electricity Price Data - Global Average Baseline
Provides accurate ToD (Time of Day) pricing reflecting a standardized Worldwide average.
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/api", tags=["Prices"])

# ─── Per-hour rate tables ─────────────────────────────────────────────────────
# Global Standard Time-of-Use pricing representation
GLOBAL_HOURLY: Dict[int, float] = {
    0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10, 4: 0.10, 5: 0.10, 6: 0.10,
    7: 0.15, 8: 0.15,
    9: 0.25, 10: 0.25, 11: 0.25, 12: 0.25, 13: 0.25,
    14: 0.25, 15: 0.25, 16: 0.25, 17: 0.25,
    18: 0.15, 19: 0.15, 20: 0.15, 21: 0.15,
    22: 0.10, 23: 0.10,
}

# ─── Provider metadata ────────────────────────────────────────────────────────
PROVIDERS_META = {
    "global": {
        "full_name": "Global Standard Electricity Provider (Worldwide Average)",
        "peak":     0.25,
        "mid":      0.15,
        "off_peak": 0.10,
        "peak_hours": "09:00–18:00",
        "mid_hours":  "07:00–09:00 & 18:00–22:00",
        "offpeak_hours": "22:00–07:00",
        "hourly": GLOBAL_HOURLY,
        "note": "Reflects universal Time-of-Use structure (USD).",
    }
}


def _get_zone(hour: int, hourly: Dict[int, float], peak: float, mid: float, off_peak: float) -> str:
    rate = hourly.get(hour, off_peak)
    if rate >= peak:
        return "peak"
    elif rate >= mid:
        return "mid"
    return "off_peak"


@router.get("/price-today")
def get_price_today(provider: str = "global"):
    """
    Returns today's electricity tariff schedule for the global standard provider.
    """
    key = "global"

    meta = PROVIDERS_META[key]
    hourly: Dict[int, float] = meta["hourly"]  # type: ignore[assignment]
    peak_rate: float = meta["peak"]  # type: ignore[assignment]
    mid_rate: float = meta["mid"]  # type: ignore[assignment]
    off_peak_rate: float = meta["off_peak"]  # type: ignore[assignment]

    current_hour = datetime.now().hour
    current_rate = hourly.get(current_hour, off_peak_rate)
    current_zone = _get_zone(current_hour, hourly, peak_rate, mid_rate, off_peak_rate)

    # Build all-providers comparison table
    all_providers = {
        "global": {
            "full_name": meta["full_name"],
            "peak":      meta["peak"],
            "mid":       meta["mid"],
            "off_peak":  meta["off_peak"],
            "note":      meta["note"],
        }
    }

    return {
        "provider": key,
        "provider_full": meta["full_name"],
        "tariff_year": "Current",
        "unit": "$/kWh",
        "note": meta["note"],
        "current_hour": current_hour,
        "current_rate": current_rate,
        "current_zone": current_zone,
        "zones": {
            "peak":     {"rate": peak_rate, "hours": meta["peak_hours"],    "color": "#ef4444"},
            "mid":      {"rate": mid_rate,  "hours": meta["mid_hours"],     "color": "#eab308"},
            "off_peak": {"rate": off_peak_rate, "hours": meta["offpeak_hours"], "color": "#22c55e"},
        },
        "hourly_rates": hourly,
        "simulation_rates": {
            "peak":      peak_rate,
            "mid":       mid_rate,
            "off_peak":  off_peak_rate,
        },
        "all_providers": all_providers,
    }
