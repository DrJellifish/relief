#!/usr/bin/env python3
"""Simulate particle drift using the latest CMEMS surface currents.

The script downloads the most recent 72 h forecast of surface currents from
Copernicus Marine based on the spatial extent of ``release_schedule_15min.csv``.
It then uses Parcels to release one particle at each unique release location and
advects them with the ocean currents (no wind forcing). Each particle carries a
``buoyancy`` variable initialised to 1.635 kg (3×545 g).

Run the script after defining ``COPERNICUSMARINE_SERVICE_USERNAME`` and
``COPERNICUSMARINE_SERVICE_PASSWORD`` in the environment. Optionally set
``SIM_START_DATE`` (``YYYY-MM-DD``) to choose the forecast start date.
"""

import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import copernicusmarine
from shapely.geometry import Point, Polygon
from parcels import AdvectionRK4, FieldSet, JITParticle, ParticleSet, Variable

# Gaza coastal polygon (approximate)
gaza_polygon = Polygon(
    [
        (34.2, 31.2),
        (34.6, 31.2),
        (34.6, 31.6),
        (34.2, 31.6),
    ]
)

# ---------------------------------------------------------------------------
# 1. Load release locations
schedule = pd.read_csv("release_schedule_15min.csv")
locations = (
    schedule.groupby("release_id")[["lat", "lon"]].first().reset_index()
)

# 2. Determine temporal window
start_time_str = schedule["release_time"].min()
start_date_str = os.environ.get(
    "SIM_START_DATE", datetime.now(timezone.utc).strftime("%Y-%m-%d")
)
start_datetime = datetime.strptime(
    f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S"
)
end_datetime = start_datetime + timedelta(hours=72)

# 3. Spatial bounds with 0.5° buffer
min_lat = locations["lat"].min() - 0.5
max_lat = locations["lat"].max() + 0.5
min_lon = locations["lon"].min() - 0.5
max_lon = locations["lon"].max() + 0.5

# 4. Verify CMEMS credentials
cmems_user = os.environ.get("COPERNICUSMARINE_SERVICE_USERNAME", "")
cmems_pwd = os.environ.get("COPERNICUSMARINE_SERVICE_PASSWORD", "")
if not cmems_user or not cmems_pwd:
    raise SystemExit(
        "Copernicus Marine credentials not set. Please define "
        "COPERNICUSMARINE_SERVICE_USERNAME and COPERNICUSMARINE_SERVICE_PASSWORD."
    )

# 5. Download currents using Copernicus Marine Toolbox
outfile = (
    f"cmems_currents_{start_datetime:%Y%m%dT%H%M%S}_"
    f"{end_datetime:%Y%m%dT%H%M%S}.nc"
)
dataset_id = "cmems_mod_med_phy-cur_anfc_4.2km_PT15M-i"
print("Downloading CMEMS currents ...")
copernicusmarine.subset(
    dataset_id=dataset_id,
    variables=["uo", "vo"],
    minimum_longitude=min_lon,
    maximum_longitude=max_lon,
    minimum_latitude=min_lat,
    maximum_latitude=max_lat,
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    output_filename=outfile,
    username=cmems_user,
    password=cmems_pwd,
)
print("Saved currents to", outfile)

# 6. Build Parcels FieldSet from the downloaded file
fieldset = FieldSet.from_netcdf(
    outfile,
    variables={"U": "uo", "V": "vo"},
    dimensions={"lon": "longitude", "lat": "latitude", "time": "time", "depth": "depth"},
    allow_time_extrapolation=True,
)

# 7. Define particle with buoyancy attribute
class BuoyantParticle(JITParticle):
    buoyancy = Variable("buoyancy", dtype=np.float32, initial=1.635)

# 8. Initialise ParticleSet at surface
pset = ParticleSet(
    fieldset=fieldset,
    pclass=BuoyantParticle,
    lon=locations["lon"].values,
    lat=locations["lat"].values,
    depth=[0.0] * len(locations),
    time=np.datetime64(start_datetime),
)

# 9. Advect particles with ocean currents only
pset.execute(
    AdvectionRK4,
    runtime=timedelta(hours=72),
    dt=timedelta(minutes=15),
)

# 10. Output final positions and count arrivals in Gaza
final_positions = [
    {"release_id": rid, "lon": p.lon, "lat": p.lat}
    for p, rid in zip(pset, locations["release_id"].values)
]

final_positions_df = pd.DataFrame(final_positions)
final_positions_df["in_gaza"] = final_positions_df.apply(
    lambda row: gaza_polygon.contains(Point(row["lon"], row["lat"])), axis=1
)

arrivals = (
    final_positions_df.groupby("release_id")["in_gaza"]
    .sum()
    .reset_index(name="particles_in_gaza")
)

print(arrivals)
final_positions_df.to_csv("final_positions.csv", index=False)
arrivals.to_csv("particles_in_gaza.csv", index=False)
