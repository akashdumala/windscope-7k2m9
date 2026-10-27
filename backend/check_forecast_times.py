import requests
from collections import Counter

url = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"

params = {
    "publishDateTimeFrom": "2025-12-30T00:00:00Z",
    "publishDateTimeTo": "2026-01-02T00:00:00Z",
}

response = requests.get(url, params=params, timeout=60)
response.raise_for_status()

records = response.json()

print("Records returned:", len(records))

jan_first = [
    row for row in records
    if row.get("startTime", "").startswith("2026-01-01")
]

print("January 1 target records:", len(jan_first))
print("\nPublication times for January 1 targets:")

print(Counter(
    row.get("publishTime")
    for row in jan_first
))

print("\nFirst 10 January 1 records:")
for row in jan_first[:10]:
    print(row)