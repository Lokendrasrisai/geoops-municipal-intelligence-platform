"""Generates sample_water_mains.csv — run once, commit the output."""
import random
import csv
from datetime import date, timedelta

random.seed(42)

MATERIALS = ["Cast Iron", "Ductile Iron", "PVC", "Steel", "Concrete", "Asbestos Cement"]
CONDITIONS = ["Excellent", "Good", "Fair", "Poor", "Critical"]
STATUSES = ["Active", "Inactive", "Active", "Active", "Active", "Abandoned"]  # weighted Active
PRESSURE_ZONES = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"]
DIAMETERS = [4, 6, 8, 10, 12, 16, 20, 24]

# Bounding box: central Illinois water utility area (realistic coords)
LAT_CENTER, LON_CENTER = 40.630, -89.720
LAT_SPREAD, LON_SPREAD = 0.060, 0.090

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

rows = []
for i in range(1, 501):
    asset_id = f"WM-{i:05d}" if random.random() > 0.05 else ""          # ~5% missing
    install_year = random.choice([
        random.randint(1945, 1985),  # older pipes — majority
        random.randint(1945, 1985),
        random.randint(1985, 2005),
        random.randint(2005, 2023),
        9999 if random.random() < 0.02 else random.randint(1945, 2023),  # ~2% future year
    ])
    condition = random.choice(CONDITIONS + ["", ""])                      # ~15% missing
    material   = random.choice(MATERIALS + [""])                          # ~10% missing
    diameter   = random.choice(DIAMETERS + [999])                        # ~10% bad value
    pressure_zone = random.choice(PRESSURE_ZONES + [""])                 # ~7% missing
    status     = random.choice(STATUSES + ["Unknown"])
    last_insp  = random_date(2018, 2024).isoformat() if random.random() > 0.12 else ""
    latitude   = round(LAT_CENTER + random.uniform(-LAT_SPREAD, LAT_SPREAD), 6)
    longitude  = round(LON_CENTER + random.uniform(-LON_SPREAD, LON_SPREAD), 6)
    length_ft  = round(random.uniform(50, 800), 1)
    rows.append([
        asset_id, install_year, condition, material, diameter,
        pressure_zone, status, last_insp, latitude, longitude, length_ft
    ])

header = [
    "asset_id", "install_year", "condition", "material", "diameter_in",
    "pressure_zone", "status", "last_inspection_date", "latitude", "longitude",
    "length_ft"
]

with open("/sessions/compassionate-brave-cerf/mnt/geoops-municipal-intelligence-platform/data/sample_water_mains.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Written {len(rows)} rows")
