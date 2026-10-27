
from flask import Blueprint, jsonify

from app.services import (
    get_dashboard_summary,
    get_health_status,
)
from app.elexon import analyse_january

api = Blueprint("api", __name__)


@api.get("/health")
def health():
    return jsonify(get_health_status())


@api.get("/dashboard/summary")
def dashboard_summary():
    return jsonify(get_dashboard_summary())


@api.get("/")
def api_info():
    return jsonify({
        "name": "WindScope API",
        "version": "1.0.0",
        "endpoints": [
            "/api/health",
            "/api/dashboard/summary",
            "/api/analysis/january-2026",
        ],
    })


@api.get("/analysis/january-2026")
def january_analysis():
    try:
        result = analyse_january()
        return jsonify(result)
    except Exception as error:
        return jsonify({
            "error": "Unable to retrieve or analyse Elexon data",
            "details": str(error),
        }), 502
