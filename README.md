# relief

This repository demonstrates an automated workflow to fetch Copernicus
Mediterranean surface current data for a 72-hour forecast window using
`motuclient`. The release schedule used for the query is included in
`release_schedule_15min.csv`.

## Downloading CMEMS Currents

Install the required packages and export your Copernicus credentials before
running the download script:

```bash
pip install -r requirements.txt
export CMEMS_USER=<your CMEMS username>
export CMEMS_PWD=<your CMEMS password>
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
publish the dashboard. Note that the hosted environment is restricted and
may not include heavy geospatial packages like `xarray` and `cartopy`.

## Trajectory Analysis

`trajectory_analysis.qmd` aggregates bottle raft trajectories and
visualizes Gaza shoreline arrivals. Render it locally or publish to Posit
Connect:

```bash
quarto render trajectory_analysis.qmd
```

## License

This project is licensed under the [MIT License](LICENSE).
