# relief

This repository demonstrates an automated workflow to fetch Copernicus Mediterranean surface current data for a 72-hour forecast window using `motuclient`. The release schedule used for the query is included in `release_schedule_15min.csv`.

## Downloading CMEMS Currents

Install the required Python packages, then run the script. Set `CMEMS_USER` and
`CMEMS_PWD` in your environment. Optionally define `SIM_START_DATE`
(YYYY-MM-DD).

```bash
pip install -r requirements.txt
python3 download_cmems_currents.py
```

## Quarto Dashboard

`currents_report.qmd` is a Quarto document that runs the downloader and displays a basic plot of the currents. Render it locally or publish to Posit Connect:

```bash
quarto render currents_report.qmd
quarto publish connect currents_report.qmd
```

Create a free account on [Posit Connect Cloud](https://connect.posit.cloud) and follow the [documentation](https://docs.posit.co/connect-cloud/) to publish the dashboard.
