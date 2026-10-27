import json
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"


def fetch_window(start, end):
    response = requests.get(
        BASE_URL,
        params={
            "publishDateTimeFrom": start,
            "publishDateTimeTo": end,
        },
        headers={"Accept": "application/json"},
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]

    raise ValueError("Unexpected WINDFOR response")


def main():
    start = datetime(2025, 12, 30, tzinfo=timezone.utc)
    end = datetime(2026, 2, 2, tzinfo=timezone.utc)

    all_records = {}

    while start < end:
        window_end = min(start + timedelta(days=1), end)

        start_text = start.isoformat().replace("+00:00", "Z")
        end_text = window_end.isoformat().replace("+00:00", "Z")

        records = fetch_window(start_text, end_text)

        print(
            f"{start_text} to {end_text}: "
            f"{len(records)} records"
        )

        for record in records:
            key = (
                record.get("publishTime"),
                record.get("startTime"),
            )
            all_records[key] = record

        start = window_end

    january_targets = {
        record.get("startTime")
        for record in all_records.values()
        if record.get("startTime", "").startswith("2026-01-")
    }

    print("\nTotal unique records:", len(all_records))
    print("Unique January target intervals:", len(january_targets))
    print("Expected January intervals: 1488")
    print(
        "Coverage:",
        round(len(january_targets) / 1488 * 100, 2),
        "%",
    )


if __name__ == "__main__":
    main()
from collections import Counter

print("\n--- FORECAST DATA DIAGNOSTICS ---")

with open("data/forecasts_sample.json", "r", encoding="utf-8") as file:
    forecast_records = json.load(file)

print("Total forecast records:", len(forecast_records))
print("Fields:", list(forecast_records[0].keys()) if forecast_records else [])

print("\nFirst 5 forecast records:")
for record in forecast_records[:5]:
    print(record)

print("\nForecast publication dates:")
print(Counter(
    record.get("publishTime", "")[:10]
    for record in forecast_records
).most_common(10))

print("\nForecast target dates:")
print(Counter(
    record.get("startTime", "")[:10]
    for record in forecast_records
).most_common(10))