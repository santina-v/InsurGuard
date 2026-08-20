import requests

URL = "https://archive-api.open-meteo.com/v1/archive"

# Chicago coordinates
LAT = 41.8781
LON = -87.6298

DATE = "2026-03-15"


response = requests.get(
    URL,
    params={
        "latitude": LAT,
        "longitude": LON,
        "start_date": DATE,
        "end_date": DATE,
        "hourly": "precipitation",
    },
    timeout=10,
)

response.raise_for_status()

data = response.json()

precipitation = data["hourly"]["precipitation"]

print("=" * 60)
print("INSURGUARD WEATHER VERIFICATION")
print("=" * 60)

print(f"Location: Chicago")
print(f"Date: {DATE}")

print("\nHourly precipitation:")

for hour, value in enumerate(precipitation):
    print(f"{hour:02d}:00 -> {value} mm")

total = sum(value or 0 for value in precipitation)

print("\nTotal precipitation:", total, "mm")

if total > 0:
    print("\n⚠ PRECIPITATION DETECTED")
else:
    print("\n✓ NO PRECIPITATION DETECTED")