# relief

This repository demonstrates an automated workflow to fetch Copernicus
Mediterranean surface current data for a 72-hour forecast window using
`motuclient`. The release schedule used for the query is included in
`release_schedule_15min.csv`.

## Downloading CMEMS Currents

Use the Python script to download the NetCDF file. Ensure `CMEMS_USER` and
`CMEMS_PWD` are set in your environment.

```bash
python3 download_cmems_currents.py
```

## Quarto Dashboard

`currents_report.qmd` is a Quarto document that executes the Python
script and displays an example map of the currents. Render it locally or
publish directly to Posit Connect:

```bash
quarto render currents_report.qmd
quarto publish connect currents_report.qmd
```

Create a free account on [Posit Connect Cloud](https://connect.posit.cloud)
and follow the [documentation](https://docs.posit.co/connect-cloud/) to
publish the dashboard.
