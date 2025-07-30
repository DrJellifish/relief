#!/usr/bin/env python3
"""Download CMEMS 72h forecast currents using motuclient.

This script reads `release_schedule_15min.csv`, determines the spatial
bounds and temporal window, then calls the `motuclient` command line
utility to download surface currents for use in drift modelling.

Set the environment variables `CMEMS_USER` and `CMEMS_PWD` with your
Copernicus Marine credentials. Optionally specify `SIM_START_DATE`
(YYYY-MM-DD) to control the forecast start date.
"""

import os
import subprocess
from datetime import datetime, timedelta, timezone
import pandas as pd

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
cmems_user = os.environ.get("CMEMS_USER", "")
cmems_pwd = os.environ.get("CMEMS_PWD", "")
if not cmems_user or not cmems_pwd:
    raise SystemExit(
        "CMEMS credentials not set. Please define CMEMS_USER and CMEMS_PWD."
    )

# 5. Build motuclient command
out_name = f"med_currents_{start_datetime:%Y%m%dT%H%M%S}_{end_datetime:%Y%m%dT%H%M%S}.nc"

motu_cmd = [
    "motuclient",
    "--motu", "https://nrt.cmems-du.eu/motu-web/Motu",
    "--service-id", "MEDSEA_ANALYSISFORECAST_PHY_006_013-TDS",
    "--product-id", "cmems_mod_med_phy_anfc_0.027deg_PT1H-m",
    "--longitude-min", str(min_lon), "--longitude-max", str(max_lon),
    "--latitude-min", str(min_lat), "--latitude-max", str(max_lat),
    "--date-min", start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    "--date-max", end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    "--depth-min", "0.494", "--depth-max", "0.494",
    "--variable", "uo", "--variable", "vo",
    "--out-dir", ".", "--out-name", out_name,
    "--user", cmems_user,
    "--pwd", cmems_pwd,
]

print("Running:", " ".join(motu_cmd))
ret = subprocess.run(motu_cmd)
if ret.returncode != 0:
    raise SystemExit(f"motuclient failed with code {ret.returncode}")

print("Downloaded currents to", out_name)
