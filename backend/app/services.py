
from datetime import datetime, timezone


def get_dashboard_summary():
    """
    Temporary demonstration data.

    Replace this service with validated Elexon data
    in the data-integration step.
    """
    return {
        "source": "illustrative",
        "is_demo": True,
        "actual_generation_mw": 8400,
        "forecast_generation_mw": 8000,
        "absolute_error_mw": 400,
        "resolution_minutes": 30,
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
    }


def get_health_status():
    return {
        "status": "ok",
        "service": "wind-forecast-api",
    }
