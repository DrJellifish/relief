import os
import pandas as pd
from datetime import datetime, timedelta
import subprocess

# Load release schedule
df = pd.read_csv('release_schedule_15min.csv')

start_time = df['release_time'].min()
start_date = os.environ.get('SIM_START_DATE', datetime.utcnow().strftime('%Y-%m-%d'))
start_dt = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M:%S')
end_dt = start_dt + timedelta(hours=72)

buffer = 0.5
min_lat = df['lat'].min() - buffer
max_lat = df['lat'].max() + buffer
min_lon = df['lon'].min() - buffer
max_lon = df['lon'].max() + buffer

out_name = f"med_currents_{start_dt.strftime('%Y%m%dT%H%M%S')}_{end_dt.strftime('%Y%m%dT%H%M%S')}.nc"

cmd = [
    'motuclient',
    '--motu', 'https://nrt.cmems-du.eu/motu-web/Motu',
    '--service-id', 'MEDSEA_ANALYSISFORECAST_PHY_006_013-TDS',
    '--product-id', 'cmems_mod_med_phy_anfc_0.027deg_PT1H-m',
    '--longitude-min', str(min_lon), '--longitude-max', str(max_lon),
    '--latitude-min', str(min_lat), '--latitude-max', str(max_lat),
    '--date-min', start_dt.strftime('%Y-%m-%d %H:%M:%S'),
    '--date-max', end_dt.strftime('%Y-%m-%d %H:%M:%S'),
    '--depth-min', '0.494', '--depth-max', '0.494',
    '--variable', 'uo', '--variable', 'vo',
    '--out-dir', '.', '--out-name', out_name,
    '--user', os.environ.get('CMEMS_USER', ''),
    '--pwd', os.environ.get('CMEMS_PWD', '')
]

print('Running command:')
print(' '.join(cmd))
res = subprocess.call(cmd)
if res != 0:
    raise SystemExit(f"motuclient failed with code {res}")
print(f"Downloaded currents to {out_name}")
