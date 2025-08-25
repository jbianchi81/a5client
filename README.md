# a5 api client library
This is a Python client library to work against a [alerta5DBIO API](https://github.com/jbianchi81/alerta5DBIO.git) instance developed by [Instituto Nacional del Agua](https://www.ina.gob.ar), such as the one deployed [here](https://alerta.ina.gob.ar/a5).
## Installation
```bash
# set environment
python3 -m venv .
source bin/activate
## Install from pip
pip install a5-client
## Or clone git repo
clone https://github.com/jbianchi81/a5client.git
cd a5client
pip install .
```
#### Config file location
- **Linux**: $HOME/.a5client.ini
- **Windows**: %USERPROFILE%/.a5client.ini 
- **MacOS**: $HOME/.a5client.ini
#### Default log file location (may be changed in config file)
- **Linux**: $HOME/.local/share/a5client/logs/a5client.log
- **Windows**: %LOCALAPPDATA%/a5client/logs/a5client.log
- **MacOS**: $HOME/Library/Logs/a5client/a5client.log
### Config file example
```
[log]
  filename = /var/log/a5client.log
[server]
  url = http://localhost:3005
  token = my.access.token
```
## Use
```python
from datetime import datetime, timedelta
from a5client import Crud
# Instantiate client
client = Crud(url="A5_API_ENDPOINT_URL", token="YOUR_PERSONAL_TOKEN")
```
### Methods
```python
# READ actions
# Retrieve observations metadata
series = client.readSeries(
    var_id=2
)

# retrieve stations metadata
stations = client.readEstaciones()

# retrieve area metadata
area = client.readArea(1)

# retrieve variable metadata
var = client.readVar(2)

# retrieve observations data
serie = client.readSerie(
    series_id=29, 
    timestart="2020-01-01T03:00:00.000Z", 
    timeend="2021-01-01T03:00:00.000Z"
)

# retrieve simulation configuration
calibrado = client.readCalibrado(289)

# retrieve forecast metadata
corridas = client.readCorridas(289)

# retrieve forecast data, only last run
serie_forecast = client.readSerieProno(
    cal_id=289,
    series_id=3526
)

# retrieve forecast data, concatenate runs
serie_forecast = client.readSeriePronoConcat(
    cal_id=289,
    series_id=3526,
    forecast_timestart = datetime.now() - timedelta(days=20)
)

# WRITE actions
# create sites (stations, areas, scenes)
created_sites = client.createSites(
    [
        {
            "nombre": "my_station_name",
            "id": 11111111,
            "geom": {
                "type": "Point",
                "coordinates": [ -55.55, -33.33 ]
            },
            "tabla": "alturas_varios"   
        }
    ],
    tipo="estaciones",
    format="json"
)

# create series
created_series = client.createSeries(
    [
        {
            "tipo": "puntual",
            "id": 22222222,
            "estacion": created_sites[0],
            "var": {"id": 2},
            "procedimiento": {"id": 1},
            "unidades": {"id": 11}
        }
    ]
)

# create observations
import pandas as pd 
observations = pd.DataFrame({
        "valor": [1.11, 2.22, 3.33]
    },
    index = pd.date_range(start="2024-01-01 00:00", periods=3, freq='h', tz="UTC")
)
created_observations = client.createObservaciones(
    observations,
    series_id = created_series[0]["id"],
    tipo="puntual"
)

# Create simulation run
from a5client import observacionesDataFrameToList
forecasts = pd.DataFrame({
        "valor": [1.21, 2.32, 3.43]
    },
    index = pd.date_range(start="2024-01-01 00:00", periods=3, freq='h', tz="UTC")
)
forecast_run = {
    "forecast_date": "2024-01-01 00:00",
    "series": [
        {
            "series_table": "series",
            "series_id": created_series[0]["id"],
            "pronosticos": observacionesDataFrameToList(forecasts, series_id=created_series[0]["id"])
        }
    ]
}
created_run = client.createCorrida(
    forecast_run,
    cal_id = 507
)
```
### Auxiliary functions
```python
from a5client import observacionesDataFrameToList, observacionesListToDataFrame, geojsonToList
from datetime import datetime
# DataFrame to list of dict (a5 schema)
observaciones = pd.DataFrame({
        "valor": [1.21, 2.32, 3.43]
    },
    index = pd.date_range(start="2024-01-01 00:00", periods=3, freq='h', tz="UTC")
)
df = observacionesDataFrameToList(observaciones, series_id = 3333333)

# list of dict (a5 schema) to DataFrame
df = observacionesListToDataFrame([
    {
        "timestart": datetime(2024,1,1,0),
        "valor": 5.55
    },
    {
        "timestart": datetime(2024,1,1,1),
        "valor": 4.44
    },
    {
        "timestart": datetime(2024,1,1,2),
        "valor": 3.33
    }
])

# GeoJSON dict to list of sites dict (a5 schema)
sites = geojsonToList({
    "type": "FeatureCollection",
    "features": [
        {
            "geometry": {
                "type": "Point",
                "coordinates": [-55.55, -33.33]
            },
            "properties": {
                "nombre": "my_station_name",
                "id": 555555,
                "tabla": "my_provider_name"
            }
        }
    ]
})
```
## TO DO
- Update methods
- Delete methods
