from jsonschema import validate as json_validate
import requests
import pandas
import os
from datetime import datetime, timedelta
import yaml
import logging
import dateutil
import pytz

import src.a5client.config as config

logfile = "%s/../../log/a5client.log" % os.path.dirname(__file__)
datadir = "%s/../../data" % os.path.dirname(__file__)

logging.basicConfig(filename= logfile, level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
logging.FileHandler(logfile,"w+")

from a5client.schemas import schemas

serie_schema = open("%s/schemas/yaml/serie.yml" % datadir)
serie_schema = yaml.load(serie_schema,yaml.CLoader)

def validate(instance,classname):
    if classname not in schemas["components"]["schemas"].keys():
        raise Exception("Invalid class")
    return json_validate(instance,schema=schemas) #[classname])

# CLASSES

class Serie():
    def __init__(self,params):
        json_validate(params,schema=serie_schema)
        self.id = params["id"] if "id" in params else None
        self.tipo = params["tipo"] if "tipo" in params else None
        self.observaciones = [Observacion(o) for o in params["observaciones"]] if "observaciones" in params else []
    def toDict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "observaciones": [o.toDict() for o in self.observaciones]
        }

class Observacion():
    def __init__(self,params):
        # json_validate(params,"Observacion")
        self.timestart = params["timestart"] if isinstance(params["timestart"],datetime) else tryParseAndLocalizeDate(params["timestart"])
        self.timeend = None if "timeend" not in params else params["timeend"] if isinstance(params["timeend"],datetime) else tryParseAndLocalizeDate(params["timeend"])
        self.valor = params["valor"]
        self.series_id = params["series_id"] if "series_id" in params else None
        self.tipo = params["tipo"] if "tipo" in params else "puntual"
        self.tag = params["tag"] if "tag" in params else None
    def toDict(self):
        return {
            "timestart": self.timestart.isoformat(),
            "timeend": self.timeend.isoformat() if self.timeend is not None else None,
            "valor": self.valor,
            "series_id": self.series_id,
            "tipo": self.tipo,
            "tag": self.tag
        }
            
# CRUD

class Crud():
    def __init__(self,params : dict={}):
        self.url = params["url"] if "url" in params else config.api_url
        self.token = params["token"] if "token" in params else config.api_token
        self.proxy_dict = params["proxy_dict"] if "proxy_dict" in params else None
    
    def getAuthorizationHeader(self):
        return {'Authorization': 'Bearer ' + self.token} if self.token is not None else None
    
    def readSeries(self,tipo="puntual",series_id=None,area_id=None,estacion_id=None,escena_id=None,var_id=None,proc_id=None,unit_id=None,fuentes_id=None,tabla=None,id_externo=None,geom=None,include_geom=None,no_metadata=None,date_range_before=None,date_range_after=None,getMonthlyStats=None,getStats=None,getPercentiles=None,percentil=None,use_proxy=False):
        if date_range_before is not None:
            date_range_before = date_range_before if isinstance(date_range_before,str) else date_range_before.isoformat()
        if date_range_after is not None:
            date_range_after =date_range_after if isinstance(date_range_after,str) else date_range_after.isoformat()
        params = locals()
        del params["use_proxy"]
        del params["tipo"]
        response = requests.get("%s/obs/%s/series" % (self.url, tipo),
            params = params,
            headers = self.getAuthorizationHeader(),
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def readSerie(self,series_id,timestart=None,timeend=None,tipo="puntual",use_proxy=False):
        params = {}
        if timestart is not None and timeend is not None:
            params = {
                "timestart": timestart if isinstance(timestart,str) else timestart.isoformat(),
                "timeend": timeend if isinstance(timeend,str) else timeend.isoformat()
            }
        response = requests.get("%s/obs/%s/series/%i" % (self.url, tipo, series_id),
            params = params,
            headers = self.getAuthorizationHeader(),
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def createObservaciones(self,data,series_id : int,column="valor",tipo="puntual", timeSupport=None,use_proxy=False):
        if isinstance(data,pandas.DataFrame):
            data = observacionesDataFrameToList(data,series_id,column,timeSupport)
        [validate(x,"Observacion") for x in data]
        url = "%s/obs/%s/series/%i/observaciones" % (self.url, tipo, series_id) if series_id is not None else "%s/obs/%s/observaciones" % (self.url, tipo)
        response = requests.post(url, json = {
                "observaciones": data
            }, headers = self.getAuthorizationHeader(),
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def createCorrida(self,data,cal_id=None,use_proxy=False):
        validate(data,"Corrida")
        cal_id = cal_id if cal_id is not None else data["cal_id"] if "cal_id" in data else None
        if cal_id is None:
            raise Exception("Missing parameter cal_id")
        url = "%s/sim/calibrados/%i/corridas" % (self.url, cal_id)
        response = requests.post(url, json = data, headers = self.getAuthorizationHeader(),
            proxies = self.proxy_dict if use_proxy else None
        )
        logging.debug("createCorrida url: %s" % response.url)
        if response.status_code != 200:
            raise Exception("request failed: status: %i, message: %s" % (response.status_code, response.text))
        json_response = response.json()
        return json_response

    def readVar(self,var_id,use_proxy=False):
        response = requests.get("%s/obs/variables/%i" % (self.url, var_id),
            headers = self.getAuthorizationHeader(),
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def readSerieProno(self,series_id,cal_id,timestart=None,timeend=None,use_proxy=False,cor_id=None,forecast_date=None,qualifier=None):
        """
        Reads prono serie from a5 API
        if forecast_date is not None, cor_id is overwritten by first corridas match
        returns Corridas object { series_id: int, cor_id: int, forecast_date: str, pronosticos: [{timestart:str,valor:float},...]}
        """
        params = {}
        if forecast_date is not None:
            corridas_response = requests.get("%s/sim/calibrados/%i/corridas" % (self.url, cal_id),
                params = {
                    "forecast_date": forecast_date if isinstance(forecast_date,str) else forecast_date.isoformat()
                },
                headers = self.getAuthorizationHeader(),
                proxies = self.proxy_dict if use_proxy else None
            )
            if corridas_response.status_code != 200:
                raise Exception("request failed: %s" % corridas_response.text)
            corridas = corridas_response.json()
            if len(corridas):
                cor_id = corridas[0]["cor_id"]
            else:
                print("Warning: series %i from cal_id %i at forecast_date %s not found" % (series_id,cal_id,forecast_date))
                return {
                "series_id": series_id,
                "pronosticos": []
            }
        if timestart is not None and timeend is not None:
            params = {
                "timestart": timestart if isinstance(timestart,str) else timestart.isoformat(),
                "timeend": timeend if isinstance(timestart,str) else timeend.isoformat(),
                "series_id": series_id
            }
        if qualifier is not None:
            params["qualifier"] = qualifier
        url = "%s/sim/calibrados/%i/corridas/last" % (self.url, cal_id)
        if cor_id is not None:
            url = "%s/sim/calibrados/%i/corridas/%i" % (self.url, cal_id, cor_id)
        response = requests.get(url,
            params = params,
            headers = self.getAuthorizationHeader(),
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        if "series" not in json_response:
            print("Warning: series %i from cal_id %i not found" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": series_id,
                "qualifier": None,
                "pronosticos": []
            }
        if not len(json_response["series"]):
            print("Warning: series %i from cal_id %i not found" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": series_id,
                "qualifier": None,
                "pronosticos": []
            }
        if "pronosticos" not in json_response["series"][0]:
            print("Warning: pronosticos from series %i from cal_id %i not found" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": json_response["series"][0]["series_id"],
                "qualifier": json_response["series"][0]["qualifier"],
                "pronosticos": []
            }
        if not len(json_response["series"][0]["pronosticos"]):
            print("Warning: pronosticos from series %i from cal_id %i is empty" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": json_response["series"][0]["series_id"],
                "qualifier": json_response["series"][0]["qualifier"],
                "pronosticos": []
            }
        json_response["series"][0]["pronosticos"] = [ { "timestart": x[0], "valor": x[2]} for x in json_response["series"][0] ["pronosticos"]] # "series_id": series_id, "timeend": x[1] "qualifier":x[3]
        return {
            "forecast_date": json_response["forecast_date"],
            "cal_id": json_response["cal_id"],
            "cor_id": json_response["cor_id"],
            "series_id": json_response["series"][0]["series_id"],
            "qualifier": json_response["series"][0]["qualifier"],
            "pronosticos": json_response["series"][0]["pronosticos"]
        }

## AUX functions

def observacionesDataFrameToList(data : pandas.DataFrame,series_id : int,column="valor",timeSupport=None):
    # data: dataframe con índice tipo datetime y valores en columna "column"
    # timeSupport: timedelta object
    if data.index.dtype.name != 'datetime64[ns, America/Argentina/Buenos_Aires]':
        data.index = data.index.map(tryParseAndLocalizeDate)
    # raise Exception("index must be of type datetime64[ns, America/Argentina/Buenos_Aires]'")
    if column not in data.columns:
        raise Exception("column %s not found in data" % column)
    data = data.sort_index()
    data["series_id"] = series_id
    data["timestart"] = data.index.map(lambda x: x.isoformat()) # strftime('%Y-%m-%dT%H:%M:%SZ') 
    data["timeend"] = data["timestart"] if timeSupport is None else data["timestart"].apply(lambda x: x + timeSupport)
    data["valor"] = data[column]
    data = data[["series_id","timestart","timeend","valor"]]
    return data.to_dict(orient="records")

def observacionesListToDataFrame(data: list, tag: str=None):
    if len(data) == 0:
        raise Exception("empty list")
    data = pandas.DataFrame.from_dict(data)
    data["valor"] = data["valor"].astype(float)
    data.index = data["timestart"].apply(tryParseAndLocalizeDate)
    data.sort_index(inplace=True)
    if tag is not None:
        data["tag"] = tag
        return data[["valor","tag"]]
    else:
        return data[["valor",]]

def createEmptyObsDataFrame(extra_columns : dict=None):
    data = pandas.DataFrame({
        "timestart": pandas.Series(dtype='datetime64[ns, America/Argentina/Buenos_Aires]'),
        "valor": pandas.Series(dtype="float")
    })
    cnames = ["valor"]
    if extra_columns is not None:
        for cname in extra_columns:
            data[cname] = pandas.Series(dtype=extra_columns[cname])
            cnames.append(cname)
    data.index = data["timestart"]
    return data [cnames]

def tryParseAndLocalizeDate(date_string,timezone='America/Argentina/Buenos_Aires') -> datetime:
    date = dateutil.parser.isoparse(date_string) if isinstance(date_string,str) else date_string
    is_from_interval = False
    if isinstance(date,dict):
        date = datetime.now() + interval2timedelta(date)
        is_from_interval = True
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        try:
            date = pytz.timezone(timezone).localize(date)
        except pytz.exceptions.NonExistentTimeError:
            logging.warning("NonexistentTimeError: %s" % str(date))
            return None
    else:
        date = date.astimezone(pytz.timezone(timezone))
    return date # , is_from_interval

def interval2timedelta(interval):
    days = 0
    seconds = 0
    microseconds = 0
    milliseconds = 0
    minutes = 0
    hours = 0
    weeks = 0
    for k in interval:
        if k == "milliseconds" or k == "millisecond":
            milliseconds = interval[k]
        elif k == "seconds" or k == "second":
            seconds = interval[k]
        elif k == "minutes" or k == "minute":
            minutes = interval[k]
        elif k == "hours" or k == "hour":
            hours = interval[k]
        elif k == "days" or k == "day":
            days = interval[k]
        elif k == "weeks" or k == "week":
            weeks = interval[k] * 86400 * 7
    return timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

## EJEMPLO
'''
import a5client.a5 as a5
import a5client.util as util
# lee serie de api a5
serie = a5.readSerie(31532,"2022-05-25T03:00:00Z","2022-06-01T03:00:00Z")
serie2 = a5.readSerie(26286,"2022-05-01T03:00:00Z","2022-06-01T03:00:00Z")
# convierte observaciones a dataframe 
obs_df = a5.observacionesListToDataFrame(serie["observaciones"]) 
obs_df2 = a5.observacionesListToDataFrame(serie["observaciones"]) 
# crea index regular
new_index = util.createRegularDatetimeSequence(obs_df.index,timedelta(days=1))
# crea index regular a partir de timestart timeend
timestart = tryParseAndLocalizeDate("1989-10-14T03:00:00.000Z")
timeend = tryParseAndLocalizeDate("1990-03-10T03:00:00.000Z")
new_index=util.createDatetimeSequence(timeInterval=timedelta(days=1),timestart=timestart,timeend=timeend,timeOffset=timedelta(hours=6))
# genera serie regular
reg_df = util.serieRegular(obs_df,timeInterval=timedelta(hours=12))
reg_df2 = util.serieRegular(obs_df2,timeInterval=timedelta(hours=12),interpolation_limit=1)
# rellena nulos con otra serie
filled_df = util.serieFillNulls(reg_df,reg_df2)
# convierte de dataframe a lista de dict
obs_list = a5.observacionesDataFrameToList(obs_df,series_id=serie["id"])
# valida observaciones
for x in obs_list:
    a5.validate(x,"Observacion")
# sube observaciones a la api a5
upserted = a5.createObservaciones(obs_df,series_id=serie["id"])
'''