
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
EXPECTED_JANUARY_HOURS = 744

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})


def parse_time(value):
    """Parse an ISO timestamp and normalize it to UTC."""
    if not value:
        return None

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def fetch_records(dataset, params):
    """Fetch records from an Elexon dataset endpoint."""
    url = f"{BASE_URL}/datasets/{dataset}/stream"

    response = SESSION.get(url, params=params, timeout=60)
    response.raise_for_status()

    payload = response.json()

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]

    raise ValueError(f"Unexpected response from {dataset}")


def fetch_january_actuals():
    """Fetch January WIND actuals and aggregate complete half-hours by hour."""
    records = fetch_records(
        "FUELHH",
        {
            "publishDateTimeFrom": "2026-01-01T00:00:00Z",
            "publishDateTimeTo": "2026-02-03T00:00:00Z",
        },
    )

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 2, 1, tzinfo=timezone.utc)

    half_hourly = {}

    for record in records:
        if record.get("fuelType") != "WIND":
            continue

        interval = parse_time(record.get("startTime"))
        generation = record.get("generation")

        if interval is None or not start <= interval < end:
            continue

        if generation is None:
            continue

        half_hourly[interval] = float(generation)

    hourly_values = {}

    for interval, generation in half_hourly.items():
        hour = interval.replace(minute=0, second=0, microsecond=0)
        hourly_values.setdefault(hour, {})[interval.minute] = generation

    # Require both the :00 and :30 readings for each hour.
    hourly_actuals = {}

    for hour, readings in hourly_values.items():
        if 0 in readings and 30 in readings:
            hourly_actuals[hour] = (readings[0] + readings[30]) / 2

    return hourly_actuals


def fetch_january_forecasts():
    """Fetch January target forecasts using daily publication windows."""
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 2, 1, tzinfo=timezone.utc)

    forecasts = []

    # Fetch each publication day separately to avoid response limits.
    publication_start = datetime(2025, 12, 30, tzinfo=timezone.utc)
    publication_end = datetime(2026, 2, 2, tzinfo=timezone.utc)

    current = publication_start

    while current < publication_end:
        next_day = current + timedelta(days=1)

        records = fetch_records(
            "WINDFOR",
            {
                "publishDateTimeFrom": current.isoformat(),
                "publishDateTimeTo": next_day.isoformat(),
            },
        )

        for record in records:
            interval = parse_time(record.get("startTime"))
            published = parse_time(record.get("publishTime"))
            generation = record.get("generation")

            if interval is None or published is None or generation is None:
                continue

            if not start <= interval < end:
                continue

            forecasts.append({
                "startTime": interval,
                "publishTime": published,
                "generation": float(generation),
            })

        current = next_day

    # Remove duplicate records, if any.
    unique = {
        (item["startTime"], item["publishTime"]): item
        for item in forecasts
    }

    return list(unique.values())



def analyse_january(cutoff_hour=12):
    """Compare hourly actual wind generation with day-ahead forecasts."""
    if not 0 <= cutoff_hour <= 23:
        raise ValueError("cutoff_hour must be between 0 and 23")

    actuals = fetch_january_actuals()
    forecasts = fetch_january_forecasts()

    latest_forecast = {}

    for forecast in forecasts:
        interval = forecast["startTime"]
        published = forecast["publishTime"]

        # Use the previous day's cutoff for each target hour.
        cutoff = (
            interval.replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=1)
            + timedelta(hours=cutoff_hour)
        )

        if published > cutoff:
            continue

        previous = latest_forecast.get(interval)
        if previous is None or published > previous["publishTime"]:
            latest_forecast[interval] = forecast

    rows = []

    for interval in sorted(actuals):
        forecast = latest_forecast.get(interval)
        if forecast is None:
            continue

        actual = actuals[interval]
        predicted = forecast["generation"]
        error = predicted - actual

        rows.append({
            "startTime": interval.isoformat(),
            "publishTime": forecast["publishTime"].isoformat(),
            "actual_mw": round(actual, 2),
            "forecast_mw": round(predicted, 2),
            "error_mw": round(error, 2),
            "absolute_error_mw": round(abs(error), 2),
            "squared_error": error ** 2,
        })

    count = len(rows)

    if count == 0:
        return {
            "period": "January 2026",
            "resolution": "Hourly",
            "cutoff_hour_utc": cutoff_hour,
            "actual_hourly_intervals": len(actuals),
            "forecast_records": len(forecasts),
            "eligible_forecast_hours": len(latest_forecast),
            "matched_intervals": 0,
            "coverage_percent": 0,
            "metrics": None,
            "rows": [],
            "warning": (
                "No matches after cutoff filtering. Inspect forecast "
                "publication times and the purchasing deadline."
            ),
        }

    mae = sum(row["absolute_error_mw"] for row in rows) / count
    rmse = (sum(row["squared_error"] for row in rows) / count) ** 0.5
    bias = sum(row["error_mw"] for row in rows) / count

    return {
        "period": "January 2026",
        "resolution": "Hourly",
        "cutoff_hour_utc": cutoff_hour,
        "actual_hourly_intervals": len(actuals),
        "forecast_records": len(forecasts),
        "eligible_forecast_hours": len(latest_forecast),
        "matched_intervals": count,
        "coverage_percent": round(count / 744 * 100, 2),
        "metrics": {
            "mae_mw": round(mae, 2),
            "rmse_mw": round(rmse, 2),
            "bias_mw": round(bias, 2),
        },
        "rows": rows,
        "warning": (
            "The 12:00 UTC previous-day cutoff is an assumption, not a "
            "confirmed client deadline. Interpret the metrics accordingly."
        ),
    }
