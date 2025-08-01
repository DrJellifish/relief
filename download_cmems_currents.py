#!/usr/bin/env python3
"""Download CMEMS 72h forecast currents using the Copernicus Marine Toolbox.

This script reads ``release_schedule_15min.csv`` to determine the spatial
bounds and temporal window for the request. It then downloads surface
currents via :mod:`copernicusmarine` for use in drift modelling.

Set the environment variables ``COPERNICUSMARINE_SERVICE_USERNAME`` and
``COPERNICUSMARINE_SERVICE_PASSWORD`` with your Copernicus Marine
credentials. Optionally specify ``SIM_START_DATE`` (``YYYY-MM-DD``) to
control the forecast start date.
"""

import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import copernicusmarine

# 1. Load release schedule
schedule = pd.read_csv("release_schedule_15min.csv")

# 2. Determine time window
start_time_str = schedule['release_time'].min()
start_date_str = os.environ.get(
    "SIM_START_DATE",
    datetime.now(timezone.utc).strftime("%Y-%m-%d")
)
start_datetime = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S")
end_datetime = start_datetime + timedelta(hours=72)

# 3. Spatial bounds with 0.5 deg buffer
min_lat = schedule['lat'].min() - 0.5
max_lat = schedule['lat'].max() + 0.5
min_lon = schedule['lon'].min() - 0.5
max_lon = schedule['lon'].max() + 0.5

# 4. Verify CMEMS credentials
cmems_user = os.environ.get("COPERNICUSMARINE_SERVICE_USERNAME", "")
cmems_pwd = os.environ.get("COPERNICUSMARINE_SERVICE_PASSWORD", "")
if not cmems_user or not cmems_pwd:
    raise SystemExit(
        "Copernicus Marine credentials not set. Please define "
        "COPERNICUSMARINE_SERVICE_USERNAME and COPERNICUSMARINE_SERVICE_PASSWORD."
    )

# 5. Download using Copernicus Marine Toolbox
out_name = (
    f"med_currents_{start_datetime:%Y%m%dT%H%M%S}_"
    f"{end_datetime:%Y%m%dT%H%M%S}.nc"
)

dataset_id = "cmems_mod_med_phy-cur_anfc_4.2km_PT15M-i"
print("Downloading with Copernicus Marine Toolbox ...")
resp = copernicusmarine.subset(
    dataset_id=dataset_id,
    variables=["uo", "vo"],
    minimum_longitude=min_lon,
    maximum_longitude=max_lon,
    minimum_latitude=min_lat,
    maximum_latitude=max_lat,
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    output_filename=out_name,
    username=cmems_user,
    password=cmems_pwd,
)

print("Downloaded currents to", resp.file_path)
