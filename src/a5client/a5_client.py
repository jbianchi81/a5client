from jsonschema import validate as json_validate
import requests
import pandas
from a5_client_utils import tryParseAndLocalizeDate
from a5_client_utils.descriptors import IntDescriptor, StringDescriptor, DatetimeDescriptor, FloatDescriptor, DictDescriptor
from a5_client_utils.types import SeriesPronoDict, CorridaDict, SeriesPronoGroupedByQualifierDict, TVP, TVPProno
import json
import os
from datetime import datetime, timedelta
# import yaml
import logging
from .config import config
log_config = config["log"]
from typing import List, Union, Literal, Optional, overload, cast, Dict, Any, Tuple, TypedDict, TypeGuard
import os
from .types import Estacion, Area, Escena, GeoJSON, Sitio, Feature
from .geojson_type_check import is_geojson

logging.basicConfig(
    filename = os.path.join(
        log_config["filename"]
    ),
    level=logging.DEBUG, 
    format="%(asctime)s:%(levelname)s:%(message)s"
)
logging.FileHandler(
    os.path.join(
        log_config["filename"]
    ),
    "w+"
)

from .a5_schemas import schemas

# serie_schema = open(
#     os.path.join(
#         os.environ["PYDRODELTA_DIR"],
#         "schemas/yaml/serie.yml"
#     )
# )
# serie_schema = yaml.load(serie_schema,yaml.CLoader)

class ObsTuple(TypedDict):
    timestart : datetime
    valor : float

def validate(
    instance : dict,
    classname : str
    ) -> None:
    """_summary_

    Args:
        instance (dict): An instance of the class to validate
        classname (str): the name of the class to validate against

    Raises:
        Exception: Invalid class if classname is not in schemas

        ValidationError: If instance does not validate against schema
    """
    if classname not in schemas["components"]["schemas"].keys():
        raise Exception("Invalid class")
    return json_validate(instance,schema=schemas) #[classname])

# parsers

SeriesTable = Literal["series", "series_areal", "series_rast"]

def is_series_table(x: str) -> TypeGuard[SeriesTable]:
    return x in {"series", "series_areal", "series_rast"}

@overload
def checkInt(data, optional : Literal[True], name : str="key") -> Optional[int]: ...
@overload
def checkInt(data, optional : Literal[False]=False, name : str="key") -> int: ...
def checkInt(data, optional : bool=False, name : str="key") -> Optional[int]:
    if data is not None:
        if not isinstance(data, int):
            raise ValueError("Invalid int for %s" % name)
        return data
    else:
        if optional:
            return None
        else:
            raise ValueError("Invalid int for %s" % name)

@overload
def checkFloat(data, optional : Literal[True], name : str="key") -> Optional[float]: ...
@overload
def checkFloat(data, optional : Literal[False]=False, name : str="key") -> float: ...
def checkFloat(data, optional : bool=False, name : str="key") -> Optional[float]:
    if data is not None:
        if not isinstance(data, float):
            try:
                fl = float(data)
            except ValueError:
                raise ValueError("Invalid float for %s" % name)
            return fl
        return data
    else:
        if optional:
            return None
        else:
            raise ValueError("Invalid float for %s" % name)


@overload
def checkStr(data, optional : Literal[True], name : str="key") -> Optional[str]: ...
@overload
def checkStr(data, optional : Literal[False]=False, name : str="key") -> str: ...
def checkStr(data, optional : bool=False, name : str="key") -> Optional[str]:
    if data is not None:
        if not isinstance(data, str):
            raise ValueError("Invalid str for %s" % name)
        return data
    else:
        if optional:
            return None
        else:
            raise ValueError("Invalid str for %s" % name)

@overload
def parseDatetime(data, optional : Literal[True], name : str="key") -> Optional[datetime]: ...
@overload
def parseDatetime(data, optional : Literal[False]=False, name : str="key") -> datetime: ...
def parseDatetime(data, optional : bool=False, name : str="key") -> Optional[datetime]:
    if data is not None:
        dt = tryParseAndLocalizeDate(data)
        if data is None:
            raise ValueError("Invalid datetime for %s" % name)
        return dt
    else:
        if optional:
            return None
        else:
            raise ValueError("Invalid datetime for %s" % name)

def parseTVPProno(data) -> TVPProno:
    if not isinstance(data, dict):
        raise ValueError("invalid pronosticos item")
    timestart = parseDatetime(data.get("timestart"),name="timestart")
    timeend = parseDatetime(data.get("timeend"),name="timeend")
    valor = checkFloat(data.get("valor"), name="valor")
    series_id = checkInt(data.get("series_id"), optional=True, name="series_id")
    qualifier = checkStr(data.get("qualifier"), optional=True, name="qualifier")
    return {
        "timestart": timestart,
        "timeend": timeend,
        "valor": valor,
        "series_id": series_id,
        "qualifier": qualifier
    }

def parseSerieProno(data: dict, cal_id : int, forecast_date : datetime) -> SeriesPronoDict:
    if not isinstance(data, dict):
        raise ValueError("invalid serie prono")
    series_table = checkStr(data.get("series_table"))
    if not is_series_table(series_table):
        raise ValueError("Invalid series_table")
    series_id = checkInt(data.get("series_id"), name="series_id")
    cor_id = checkInt(data.get("cor_id"), name='cor_id')
    pronosticos_ = data.get("pronosticos")
    if not isinstance(pronosticos_, list):
        raise ValueError("Invalid pronosticos")
    pronosticos = [ parseTVPProno(p) for p in pronosticos_]
    var_id = checkInt(data.get("var_id"), optional=True, name="var_id")
    begin_date = parseDatetime(data.get("begin_date"),optional=True)
    end_date  = parseDatetime(data.get("end_date"),optional=True)
    qualifiers_ = data.get("qualifiers")
    qualifiers : Optional[List[str]]
    if qualifiers_ is not None:
        if not isinstance(qualifiers_, list):
            raise ValueError("Invalid qualifiers")
        qualifiers = []
        for q in qualifiers_:
            if not isinstance(q, str):
                raise ValueError("Invalid qualifier")
            qualifiers.append(q)
    else:
        qualifiers = None    
    count = checkInt(data.get("count"), optional=True, name="count")
    estacion_id = checkInt(data.get("estacion_id"), optional=True, name="estacion_id")
    return {
        "cal_id": cal_id,
        "forecast_date": forecast_date,
        "series_table": series_table,
        "series_id": series_id,
        "cor_id": cor_id,
        "pronosticos": pronosticos,
        "var_id": var_id,
        "begin_date": begin_date,
        "end_date": end_date,
        "qualifier": None,
        "qualifiers": qualifiers,
        "count": count,
        "estacion_id": estacion_id
    }

def parseCorrida(data: dict) -> CorridaDict:
    id_ = data.get("id")
    if not isinstance(id_, int):
        raise ValueError("invalid id")
    id : int = id_
    fd = data.get("forecast_date")
    if not isinstance(fd, str):
        raise ValueError("invalid forecast_date")
    fd_ = tryParseAndLocalizeDate(fd)
    if fd_ is None:
        raise ValueError("Invalid forecast_date")
    forecast_date : datetime = fd_
    series_ = data.get("series")
    if not isinstance(series_, list):
        raise ValueError("Invalid series")
    series = series_
    series_parsed = []
    for serie_ in series:
        serie = parseSerieProno(serie_, cal_id=id, forecast_date=forecast_date)
        series_parsed.append(serie)
    return {
        "id": id,
        "forecast_date": forecast_date,
        "series": series_parsed
    }


# CLASSES

class Observacion():
    """Represents a time-value pair of an observed variable"""

    timestart = DatetimeDescriptor() # util.tryParseAndLocalizeDate(params["timestart"])
    """begin timestamp of the observation"""

    valor = FloatDescriptor()
    """value of the observation"""
    
    timeend = DatetimeDescriptor() # (None, False) if "timeend" not in params else util.tryParseAndLocalizeDate(params["timeend"])
    """end timestamp of the observation"""

    series_id = IntDescriptor()
    """Series identifier"""

    tipo = StringDescriptor()
    """Series geometry type (puntual, areal, raster)"""

    tag = StringDescriptor()
    """Observation tag"""

    def __init__(
        self,
        timestart : Union[datetime, str],
        valor : float,
        timeend : Optional[Union[datetime,str]] = None,
        series_id : Optional[int] = None,
        tipo : str = "puntual",
        tag : Optional[str] = None
    ):
        """
        Args:
            timestart (datetime): begin timestamp of the observation
            valor (float): value of the observation
            timeend (datetime, optional): end timestamp of the observation. Defaults to None.
            series_id (int, optional): Series identifier. Defaults to None.
            tipo (str, optional): Series geometry type (puntual, areal, raster) . Defaults to "puntual".
            tag (str, optional): Observation tag. Defaults to None.
        """
        # json_validate(params,"Observacion")
        parsed_ts = tryParseAndLocalizeDate(timestart)
        if parsed_ts is None:
            raise Exception("Invalid timestart")
        self.timestart = parsed_ts
        self.timeend = tryParseAndLocalizeDate(timeend) if timeend is not None else None
        self.valor = valor
        self.series_id = series_id
        self.tipo = tipo
        self.tag = tag

    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "timestart": self.timestart.isoformat(),
            "timeend": self.timeend.isoformat() if self.timeend is not None else None,
            "valor": self.valor,
            "series_id": self.series_id,
            "tipo": self.tipo,
            "tag": self.tag
        }

class Serie():
    """Represents a timeseries of a variable in a site, obtained through a method, and measured in a units"""

    id = IntDescriptor()
    """Identifier"""

    tipo = StringDescriptor()
    """Geometry type: puntual, areal, raster"""

    @property
    def observaciones(self) -> List[Observacion]:
        """Observations"""
        return self._observaciones
    @observaciones.setter
    def observaciones(
        self,
        observaciones : List[dict] = []
    ) -> None:
        self._observaciones = [o if isinstance(o,Observacion) else Observacion(**o) for o in observaciones]

    def __init__(
        self,
        id : Optional[int] = None,
        tipo : Optional[str] = None,
        observaciones : List[dict] = []
        ):
        """
        Args:
            id (int, optional): Identifier. Defaults to None.
            tipo (str, optional): Geometry type: puntual, areal, raster. Defaults to None.
            observaciones (List[dict], optional): Observations. Each dict must have timestart (datetime) and valor (float). Defaults to [].
        """
        json_validate({"id": id, "tipo": tipo, "observaciones": observaciones}, schema=schemas) # serie_schema)
        self.id = id
        self.tipo = tipo
        self.observaciones = observaciones
    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "observaciones": [o.toDict() for o in self.observaciones]
        }
            
# CRUD

class Crud():
    """a5 api client"""

    url = StringDescriptor()
    """api url"""

    token = StringDescriptor()
    """ api authorization token"""

    proxy_dict = DictDescriptor()
    """proxy parameters"""

    timeout_connect = IntDescriptor()

    timeout_response = IntDescriptor()

    @property
    def request_headers(self):
        """API authorisation header"""
        return { "Authorization": "Bearer %s" % self.token } if self.token is not None else None

    def __init__(
        self,
        url : str,
        token : str,
        proxy_dict : Optional[Dict[str,str]] = None,
        timeout_connect : Optional[int] = 10,
        timeout_response : Optional[int] = 500
        ):
        """
        Args:
            url (str): api url
            token (str): api authorization token
            proxy_dict (dict, optional): proxy parameters. Defaults to None.
        """
        self.url = url
        self.token = token
        self.proxy_dict = proxy_dict
        self.timeout_connect = timeout_connect
        self.timeout_response = timeout_response        

    def readEstaciones(
        self,
        fuentes_id : Optional[int] = None,
        nombre : Optional[str] = None,
        unid  : Optional[int] = None,
        id  : Optional[int] = None,
        id_externo : Optional[str] = None,
        distrito : Optional[str] = None,
        pais : Optional[str] = None,
        has_obs : Optional[bool] = None, 
        real  : Optional[bool] = None,
        habilitar : Optional[bool] = None,
        tipo : Optional[str] = None,
        has_prono : Optional[bool] = None, 
        rio  : Optional[str] = None,
        tipo_2  : Optional[str] = None,
        geom  : Optional[Union[str,dict]] = None,
        propietario  : Optional[str] = None,
        automatica : Optional[bool] = None, 
        ubicacion  : Optional[str] = None,
        localidad  : Optional[str] = None,
        tabla  : Optional[str] = None,
        get_drainage_basin : Optional[bool] = None,
        use_proxy : bool = False
    ):
        if geom is not None and type(geom) == dict:
            geom = json.dumps(geom)
        params = locals()
        del params["use_proxy"]
        response = requests.get("%s/obs/puntual/estaciones" % (self.url),
            params = params,
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response
    
    def readSeries(
        self,
        tipo : str = "puntual",
        series_id : Optional[int] = None,
        area_id : Optional[int] = None,
        estacion_id : Optional[int] = None,
        escena_id : Optional[int] = None,
        var_id : Optional[int] = None,
        proc_id : Optional[int] = None,
        unit_id : Optional[int] = None,
        fuentes_id : Optional[int] = None,
        tabla : Optional[str] = None,
        id_externo : Optional[str] = None,
        geom : Optional[Union[str,dict]] = None,
        include_geom : Optional[bool] = None,
        no_metadata : Optional[bool] = None,
        date_range_before : Optional[Union[datetime,str]] = None,
        date_range_after : Optional[Union[datetime,str]] = None,
        getMonthlyStats : Optional[bool] = None,
        getStats : Optional[bool] = None,
        getPercentiles : Optional[bool] = None,
        percentil : Optional[float] = None,
        use_proxy : bool = False
        ) -> dict:
        """Retrieve series

        Args:
            tipo (str, optional): series type: puntual, areal, raster. Defaults to "puntual".
            series_id (int, optional): Series identifier. Defaults to None.
            area_id (int, optional): Area identifier (with tipo=areal). Defaults to None.
            estacion_id (int, optional): Estacion identifier (with tipo=puntual). Defaults to None.
            escena_id (int, optional): Escena identifier (with tipo=raster). Defaults to None.
            var_id (int, optional): Variable identifier. Defaults to None.
            proc_id (int, optional): Procedure identifier. Defaults to None.
            unit_id (int, optional): Unit identifier. Defaults to None.
            fuentes_id (int, optional): Fuente (source) identifier (with tipo=areal or tipo=raster). Defaults to None.
            tabla (str, optional): Network identifier (with tipo="puntual"). Defaults to None.
            id_externo (str, optional): External station identifier (with tipo=puntual). Defaults to None.
            geom (Union[str,dict], optional): Bounding box. Defaults to None.
            include_geom (bool, optional): Include geometry in response. Defaults to None.
            no_metadata (bool, optional): Exclude metadata from response. Defaults to None.
            date_range_before (datetime, optional): Only retrieve series starting before this date. Defaults to None.
            date_range_after (datetime, optional): Only retrieve series ending after this date. Defaults to None.
            getMonthlyStats (bool, optional): retrieve monthly statistics. Defaults to None.
            getStats (bool, optional): Retrieve statistics. Defaults to None.
            getPercentiles (bool, optional): Retrieve percentiles. Defaults to None.
            percentil (float, optional): Percentile [0-1]. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            data : dict. Api response. Retrieved series list is in data["rows"]
        """
        if date_range_before is not None:
            date_range_before = date_range_before if isinstance(date_range_before,str) else date_range_before.isoformat()
        if date_range_after is not None:
            date_range_after = date_range_after if isinstance(date_range_after,str) else date_range_after.isoformat()
        params = locals()
        del params["use_proxy"]
        del params["tipo"]
        del params["self"]
        response = requests.get("%s/obs/%s/series" % (self.url, tipo),
            params = params,
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def readAreas(
            self,
            area_id : Union[int,List[int],None]=None,
            unid : Union[int,List[int],None]=None,
            id : Union[int,List[int],None]=None,
            nombre : Union[str,List[str],None]=None,
            exutorio : Union[str,None]=None,
            exutorio_id : Union[int,List[int],None]=None,
            geom : Union[str,None]=None,
            tabla : Union[str,None]=None,
            pagination : Union[bool,None]=None,
            limit : Union[int,None]=None,
            offset : Union[int,None]=None,
            use_proxy : bool = False,
            no_geom : bool = False,
            format : Literal["json", "geojson"] = "json"
    ) -> Union[dict,List[dict]]:
        params = {
            "unid": area_id or unid or id,
            "exutorio": exutorio,
            "exutorio_id": exutorio_id,
            "geom": geom,
            "tabla": tabla,
            "pagination": pagination,
            "limit": limit,
            "offset": offset,
            "no_geom": no_geom,
            "format": format
        }
        response = requests.get("%s/obs/areal/areas" % (self.url),
            params = params,
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed for area id: %s. message: %s" % (area_id, response.text))
        json_response = response.json()
        return json_response


    def readArea(
        self,
        area_id : int,
        use_proxy : bool = False,
        no_geom : bool = False
    ) -> dict:
        """
        Retrieve area
        
        Args:
            area_id : int - area identifier
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.
            no_metadata (bool, optional): Don't retrieve geometry. Defaults to False
                
        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: raw area dict
        """
        params = {
            "no_geom": no_geom
        }
        response = requests.get("%s/obs/areal/areas/%i" % (self.url, area_id),
            params = params,
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed for area id: %s. message: %s" % (area_id, response.text))
        json_response = response.json()
        return json_response

    @overload
    def createSites(
        self,
        data : GeoJSON,
        tipo : Literal["estaciones","areas","escenas"],
        format : Literal["geojson"],
        use_proxy: bool = False
    ) -> list: ...
    @overload
    def createSites(
        self,
        data : Union[List[Area], List[Estacion], List[Escena]],
        tipo : Literal["estaciones","areas","escenas"],
        format : Literal["json"],
        use_proxy: bool = False
    ) -> list: ...
    def createSites(
        self,
        data : Union[List[Area], List[Estacion], List[Escena], GeoJSON],
        tipo : Literal["estaciones","areas","escenas"],
        format : Literal["json","geojson"],
        use_proxy : bool = False
    ) -> list:
        """Create or updates stations, areas or scenes

        If format=geojson, data must be a geojson dict 
        
        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: create/updated stations list"""
        if format.lower() == "geojson":
            if not is_geojson(data):
                raise ValueError("Invalid GeoJSON format")
            validate(cast(dict,data), "GeoJSON")
            data = geojsonToList(cast(GeoJSON,data))
        if tipo == "estaciones":
            [validate(cast(dict,x), "Estacion") for x in data]
            url = "%s/obs/puntual/estaciones" % (self.url)
        elif tipo == "areas":
            [validate(cast(dict,x), "Area") for x in data]
            url = "%s/obs/areal/areas" % (self.url)
        else:
            [validate(cast(dict,x), "Escena") for x in data]
            url = "%s/obs/raster/escenas" % (self.url)
        body = {}
        body[tipo] = data
        logging.debug("body head: %s" % json.dumps(body)[:200])
        response = requests.post(
            url, 
            json = body, 
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        if not len(json_response):
            raise Exception("Nothing created")
        return json_response

    def readSerie(
        self,
        series_id : int,
        timestart : Optional[datetime] = None,
        timeend : Optional[datetime] = None,
        tipo : str = "puntual",
        use_proxy : bool = False,
        no_metadata : bool = False,
        include_partial_time_intersection : bool = False
        ) -> dict:
        """Retrieve serie

        Args:
            series_id (int): Series identifier
            timestart (datetime, optional): Begin timestamp. Defaults to None.
            timeend (datetime, optional): End timestamp. Defaults to None.
            tipo (str, optional): Geometry type: puntual, areal, raster. Defaults to "puntual".
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.
            no_metadata (bool, optional): Don't retrieve metadata (only data and identifiers). Defaults to False
            include_partial_overlap (bool, optional): Retrieve observations with partial time support overlap with requested period. Defaults to False

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: raw serie dict
        """
        params : Dict[str, Any] = {
            "no_metadata": no_metadata,
            "include_partial_time_intersection": include_partial_time_intersection
        }
        if timestart is not None and timeend is not None:
            params["timestart"] = timestart if isinstance(timestart,str) else timestart.isoformat()
            params["timeend"] = timeend if isinstance(timeend,str) else timeend.isoformat()
        response = requests.get("%s/obs/%s/series/%i" % (self.url, tipo, series_id),
            params = params,
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed for series tipo: %s, id: %s. message: %s" % (tipo, series_id, response.text))
        json_response = response.json()
        return json_response
    
    def createSeries(
            self,
            data : list,
            # column : str= "valor",
            update_obs : bool = True,
            tipo : str = "puntual", 
            # timeSupport : timedelta = None,
            use_proxy : bool = False,
            series_metadata : bool = False
    ) -> list:
        """create or update series
        
        Parameters:

            data : list
                List of series to create
            
            update_obs : bool = True
                insert/update observations contained in the series items 
            
            tipo : str = "puntual"
                series type ("puntual","areal","raster")
            
            use_proxy : bool = False    
                Use proxy settings
            
            series_metadata : bool = False
                Attempt to create metadata elements (estacion, variable, procedimiento, unidades, fuente) if missing in database

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            list: list of created series"""
        [validate(x,"Serie") for x in data]
        url = "%s/obs/%s/series" % (self.url, tipo)
        response = requests.post(
            url,
            json = {
                "series": data
            },
            params = {
                "update_obs": update_obs,
                "series_metadata": series_metadata
            },
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def createObservaciones(
        self,
        data : Union[pandas.DataFrame, list],
        series_id : Union[int,None]=None,
        column : str= "valor",
        tipo : str = "puntual", 
        timeSupport : Optional[timedelta] = None,
        use_proxy : bool = False
        ) -> list:
        """Create observations

        Args:
            data (Union[pandas.DataFrame, list]): Observations DataFrame or list
            series_id (int): series identifier
            column (str, optional): If data is a DataFrame, name of the column containing the values. Defaults to "valor".
            tipo (str, optional): geometry type (puntual, areal, raster). Defaults to "puntual".
            timeSupport (timedelta, optional): Observation time support. Used to set timeend. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            list: list of created observations
        """
        if isinstance(data,pandas.DataFrame):
            data = observacionesDataFrameToList(data,series_id,column,timeSupport)
        [validate(x,"Observacion") for x in data]
        url = "%s/obs/%s/series/%i/observaciones" % (self.url, tipo, series_id) if series_id is not None else "%s/obs/%s/observaciones" % (self.url, tipo)
        response = requests.post(url, json = {
                "observaciones": data
            }, headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response
    


    def readCalibrado(
        self,
        cal_id : int,
        use_proxy : bool = False
        ) -> dict:
        """Retrieve simulation configuration ("calibrado")

        Args:
            cal_id (int): Identifier
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: _description_
        """
        url = "%s/sim/calibrados/%i" % (self.url, cal_id)
        response = requests.get(url,headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: status: %i, message: %s" % (response.status_code, response.text))
        json_response = response.json()
        return json_response

    def createCorrida(
        self,
        data : dict,
        cal_id : Optional[int] = None,
        use_proxy : bool = False
        ) -> dict:
        """Create simulation run

        Args:
            data (dict): Must validate against Corrida schema
            cal_id (int, optional): simulation configuration identifier. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: if cal_id is missing from args and from data
            Exception: Request failed if response status code is not 200

        Returns:
            dict: created simulation run
        """
        validate(data,"Corrida")
        cal_id = cal_id if cal_id is not None else data["cal_id"] if "cal_id" in data else None
        if cal_id is None:
            raise Exception("Missing parameter cal_id")
        url = "%s/sim/calibrados/%i/corridas" % (self.url, cal_id)
        response = requests.post(url, json = data, headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        logging.debug("createCorrida url: %s" % response.url)
        if response.status_code != 200:
            raise Exception("request failed: status: %i, message: %s" % (response.status_code, response.text))
        json_response = response.json()
        return json_response

    def readVar(
        self,
        var_id : int,
        use_proxy : bool = False
        ) -> dict:
        """Retrieve variable

        Args:
            var_id (int): Identifier
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: the retrieved variable
        """
        response = requests.get("%s/obs/variables/%i" % (self.url, var_id),
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def readSerieProno(
        self,
        series_id : Optional[int] = None,
        cal_id : Optional[int] = None,
        timestart : Optional[datetime] = None,
        timeend : Optional[datetime] = None,
        use_proxy : bool = False,
        cor_id : Optional[int] = None,
        forecast_date : Optional[datetime] = None,
        qualifier : Optional[str] = None,
        forecast_timestart : Optional[datetime] = None,
        tipo : Optional[str] = None,
        estacion_id : Optional[int] = None,
        var_id : Optional[int] = None,
        archived : bool = False
        ) -> SeriesPronoDict:
        """
        Reads prono serie from a5 API
        if forecast_date is not None, cor_id is overwritten by first corridas match
        returns Corridas object { series_id: int, cor_id: int, forecast_date: str, pronosticos: [{timestart:str,valor:float},...]}
        If series_id is not set, estacion_id and var_id must be set

        Args:
            series_id (int): series identifier
            cal_id (int): simulation configuration identifier
            timestart (datetime, optional): begin timestamp. Defaults to None.
            timeend (datetime, optional): end timestamp. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.
            cor_id (int, optional): simulation run identifier. Defaults to None.
            forecast_date (datetime, optional): execution timestamp. Defaults to None.
            qualifier (str, optional): simulations qualifier (used to discriminate between simulations of the same series and timestamp, for example, from different ensemble members). Defaults to None. If 'all', returns all qualifiers (not only the first match). In the latter case, 'pronosticos' property of the return value is a list of dicts (one for each qualifier) with:
            - qualifier : str
            - pronosticos : list of time-value pairs
            tipo (str, optional): series geometry type: puntual (default), areal, rast
            estacion_id (int): station identifier
            var_id (int): variable (observed property) identifier
            archived (bool): read archived forecasts, defaults to False
            

        Raises:
            Exception: Request failed if status code is not 200
            FileNotFoundError: No forecast series found

        Returns:
            dict : a forecast run 
        """
        if cal_id is None:
            raise ValueError("cal_id must be set")
        if series_id is None and (estacion_id is None or var_id is None):
            raise ValueError("If series_id is not set, estacion_id and var_id must be set")
        params = {
            "series_id": series_id,
            "tipo": tipo,
            "group_by_qualifier": True,
            "var_id": var_id,
            "estacion_id": estacion_id
        }
        if forecast_date is not None:
            corridas_response = requests.get("%s/sim/calibrados/%i/%s" % (self.url, cal_id, "corridas guardadas" if archived else "corridas"),
                params = {
                    "forecast_date": forecast_date if isinstance(forecast_date,str) else forecast_date.isoformat(),
                    "group_by_qualifier": True
                },
                headers = self.request_headers,
                proxies = self.proxy_dict if use_proxy else None,
                timeout=(self.timeout_connect,self.timeout_response)
            )
            if corridas_response.status_code != 200:
                raise Exception("request failed: %s" % corridas_response.text)
            corridas = corridas_response.json()
            if len(corridas):
                cor_id = corridas[0]["cor_id"]
            else:
                if series_id is None:
                    raise FileNotFoundError("Series not found for cal_id %i at forecast_date %s, var_id %i, estacion_id %i" % (cal_id, forecast_date, var_id, estacion_id))
                else: 
                    raise FileNotFoundError("Series %i from cal_id %i at forecast_date %s not found" % (series_id,cal_id,forecast_date))
        elif forecast_timestart is not None:
            corridas_response = requests.get("%s/sim/calibrados/%i/%s" % (self.url, cal_id, "corridas_guardadas" if archived else "corridas"),
                params = {
                    "series_id": series_id,
                    "tipo": tipo,
                    "forecast_timestart": forecast_timestart if isinstance(forecast_timestart,str) else forecast_timestart.isoformat(),
                    "includeProno": False,
                    "group_by_qualifier": True
                },
                headers = self.request_headers,
                proxies = self.proxy_dict if use_proxy else None,
                timeout=(self.timeout_connect,self.timeout_response)
            )
            if corridas_response.status_code != 200:
                raise Exception("request failed: %s" % corridas_response.text)
            corridas = corridas_response.json()
            if len(corridas):
                cor_id = corridas[len(corridas)-1]["cor_id"] if "cor_id" in corridas[len(corridas)-1] else corridas[len(corridas)-1]["id"]
            else:
                if series_id is None:
                    raise FileNotFoundError("Forecast run with cal_id %i at forecast_date greater than %s, var_id %i, estacion_id %i not found" % (cal_id, forecast_timestart, var_id, estacion_id))
                else: 
                    raise FileNotFoundError("Forecast run for series %i from cal_id %i at forecast_date greater than %s not found" % (series_id,cal_id,forecast_timestart))
        if timestart is not None and timeend is not None:
            params["timestart"] = timestart if isinstance(timestart,str) else timestart.isoformat()
            params["timeend"] = timeend if isinstance(timestart,str) else timeend.isoformat()
        if qualifier is not None and qualifier != 'all':
            params["qualifier"] = qualifier
        params["includeProno"] = True
        if cor_id is not None:
            url = "%s/sim/calibrados/%i/%s/%i" % (self.url, cal_id, "corridas_guardadas" if archived else "corridas", cor_id)
        else:
            if archived:
                raise ValueError("missing cor_id")
            url = "%s/sim/calibrados/%i/corridas/last" % (self.url, cal_id)
        response = requests.get(url,
            params = params,
            headers = self.request_headers,
            proxies = self.proxy_dict if use_proxy else None,
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        if type(json_response) == list:
            json_response = json_response[0]
        try:
            data = parseCorrida(json_response)
        except ValueError as e:
            raise ValueError(f"Invalid data returned from server: {e}")
        if "series" not in data:
            if series_id is None:
                raise FileNotFoundError("Series with cal_id %i, var_id %i, estacion_id %i" % (cal_id, var_id, estacion_id))
            else: 
                raise FileNotFoundError("Series %i from cal_id %i" % (series_id,cal_id))
        if not len(data["series"]):
            if series_id is None:
                raise FileNotFoundError("Series with cal_id %i, var_id %i, estacion_id %i" % (cal_id, var_id, estacion_id))
            else: 
                raise FileNotFoundError("Series %i from cal_id %i" % (series_id,cal_id))
        
        if qualifier is not None and qualifier == 'all':
            pronosticos = []
            qualifiers = []
            for member in data["series"]:
                pronosticos.append({
                    "qualifier": member["qualifier"],
                    "pronosticos": member["pronosticos"]
                })
                qualifiers.append(member["qualifier"])
            return {
                "forecast_date": data["forecast_date"],
                "cal_id": data["id"],
                "cor_id": data["id"] if "id" in data else data["cor_id"],
                "series_id": data["series"][0]["series_id"],
                "tipo": getSeriesTipo(data["series"][0]["series_table"]),
                "series_table": data["series"][0]["series_table"],
                "qualifiers": qualifiers,
                "qualifier": None,
                "pronosticos": pronosticos
            }
        if "pronosticos" not in data["series"][0]:
            logging.warning("Pronosticos from series %i from cal_id %i not found" % (series_id,cal_id))
            return {
                "forecast_date": data["forecast_date"],
                "cal_id": data["id"],
                "cor_id": data["id"] if "id" in data else data["cor_id"],
                "series_id": data["series"][0]["series_id"],
                "tipo": getSeriesTipo(data["series"][0]["series_table"]),
                "qualifier": data["series"][0]["qualifier"],
                "series_table": data["series"][0]["series_table"],
                "pronosticos": []
            }
        if not len(data["series"][0]["pronosticos"]):
            logging.warning("Pronosticos from series %i from cal_id %i is empty" % (series_id,cal_id))
            return {
                "forecast_date": data["forecast_date"],
                "cal_id": data["id"],
                "cor_id": data["id"] if "id" in data else data["cor_id"],
                "series_id": data["series"][0]["series_id"],
                "tipo": getSeriesTipo(data["series"][0]["series_table"]),
                "qualifier": data["series"][0]["qualifier"],
                "series_table": data["series"][0]["series_table"],
                "pronosticos": []
            }
        # data["series"][0]["pronosticos"] = [ observacionTupleToDict(x) for x in data["series"][0]["pronosticos"]] # "series_id": series_id, "timeend": x[1] "qualifier":x[3]
        return {
            "forecast_date": data["forecast_date"],
            "cal_id": data["id"],
            "cor_id": data["id"] if "id" in data else data["cor_id"],
            "series_id": data["series"][0]["series_id"],
            "qualifier": data["series"][0]["qualifier"] if "qualifier" in data["series"][0] else None,
            "series_table": data["series"][0]["series_table"],
            "pronosticos": data["series"][0]["pronosticos"]
        }
    
    def readCorridas(
        self,
        cal_id : int,
        series_id : Optional[int] = None,
        forecast_timestart : Optional[datetime] = None,
        forecast_timeend : Optional[datetime] = None,
        qualifier : Optional[str] = None,
        includeProno : bool = False,
        group_by_qualifier : bool = False,
        tipo : Optional[str] = None,
        archived : bool = False
        ) -> List[CorridaDict]:
        response = requests.get(
            "%s/sim/calibrados/%i/%s" % (self.url, cal_id, "corridas_guardadas" if archived else "corridas"),
            params = {
                'series_id': series_id,
                'tipo': tipo,
                'qualifier': qualifier,
                'includeProno': includeProno,
                'forecast_timestart': forecast_timestart.isoformat() if isinstance(forecast_timestart,datetime) else forecast_timestart,
                'forecast_timeend': forecast_timeend.isoformat() if isinstance(forecast_timeend,datetime) else forecast_timeend,
                "group_by_qualifier": group_by_qualifier
            },
            headers = {
                'Authorization': 'Bearer ' + self.token
            },
            timeout=(self.timeout_connect,self.timeout_response)
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        return response.json()

    @overload
    def readSeriePronoConcat(
        self,
        cal_id : int,
        series_id : int,
        qualifier : Optional[str] = None,
        forecast_timestart : Optional[datetime] = None,
        forecast_timeend : Optional[datetime] = None,
        tipo : Optional[Literal["puntual","areal","raster"]] = None,
        *,
        group_by_qualifier : Literal[True]
        ) -> SeriesPronoGroupedByQualifierDict: ...
    @overload
    def readSeriePronoConcat(
        self,
        cal_id : int,
        series_id : int,
        qualifier : Optional[str] = None,
        forecast_timestart : Optional[datetime] = None,
        forecast_timeend : Optional[datetime] = None,
        tipo : Optional[Literal["puntual","areal","raster"]] = None,
        *,
        group_by_qualifier : Literal[False] = False
        ) -> SeriesPronoDict: ...
    def readSeriePronoConcat(
        self,
        cal_id : int,
        series_id : int,
        qualifier : Optional[str] = None,
        forecast_timestart : Optional[datetime] = None,
        forecast_timeend : Optional[datetime] = None,
        tipo : Optional[Literal["puntual","areal","raster"]] = None,
        group_by_qualifier : bool = False
        ) -> Union[SeriesPronoDict, SeriesPronoGroupedByQualifierDict]:
        """Retrieves history of forecast runs and concatenates into a single series (newer runs overwrite older runs). If qualifier is not set and multiple qualifiers exist, a mixed qualifier series is returned unless group_by_qualifier is set to True"""
        corridas = self.readCorridas(
            cal_id,
            series_id = series_id,
            forecast_timestart = forecast_timestart, 
            forecast_timeend = forecast_timeend,
            qualifier = qualifier,
            includeProno = True,
            group_by_qualifier = True,
            tipo = tipo)
        # logging.debug('Cantidad total de corridas: ',len(corridas))
        qualifiers = {}
        if not len(corridas):
            raise FileNotFoundError("Runs not found for the specified filters")
        last_forecast_date = corridas[len(corridas)-1]["forecast_date"]
        for corrida in sorted(corridas, key = lambda c: c["forecast_date"]):
            last_forecast_date = corrida["forecast_date"]
            for serie in corrida["series"]:
                qualifier = serie["qualifier"] if "qualifier" in serie else "no_qualifier"
                if qualifier not in qualifiers:
                    qualifiers[qualifier] = {}
                for pronostico in serie["pronosticos"]:
                    ts = pronostico["timestart"]
                    prono = {
                        **pronostico,
                        "cor_id": corrida["id"] if "id" in corrida else corrida["cor_id"],
                        "forecast_date": corrida["forecast_date"]
                    }
                    qualifiers[qualifier][ts] = prono
        pronosticos = []
        if group_by_qualifier:
            return {
                "cal_id": cal_id,
                "series_id": series_id,
                "tipo": tipo,
                "series_table": get_series_table(tipo),
                "forecast_timestart": forecast_timestart,
                "forecast_timeend": forecast_timeend,
                "pronosticos": [ {"qualifier": q, "pronosticos": [ obs for ts, obs in serie.items()]} for q, serie in qualifiers.items() ],
                "forecast_date": last_forecast_date
            }    
        for qualifier, pronos in qualifiers.items():
            for timestart, prono in pronos.items():
                pronosticos.append({
                    **prono,
                    "qualifier": qualifier if qualifier != "no_qualifier" else None
                })
        return {
            "cal_id": cal_id,
            "series_id": series_id,
            "tipo": tipo,
            "series_table": get_series_table(tipo),
            "qualifier": qualifier,
            "forecast_timestart": forecast_timestart,
            "forecast_timeend": forecast_timeend,
            "pronosticos": pronosticos,
            "forecast_date": last_forecast_date
        }

## Default client
client = Crud(**config["server"])

## AUX functions

def observacionesDataFrameToList(
    data : pandas.DataFrame,
    series_id : Union[int,None]=None,
    column : str = "valor",
    timeSupport : Optional[timedelta] = None
    ) -> List[dict]:
    """Convert Observations DataFrame to list of dict

    Args:
        data (pandas.DataFrame): dataframe con índice tipo datetime y valores en columna "column"
        series_id (int): Series identifier. If None, series_id column must be in data
        column (str, optional): Column that contains the values. Defaults to "valor".
        timeSupport (timedelta, optional): Time support of the observation. Used to set timeend. Defaults to None.

    Raises:
        Exception: Column column not found in data

    Returns:
        List[dict]: Observations
    """
    # data: dataframe con índice tipo datetime y valores en columna "column"
    # timeSupport: timedelta object
    if series_id:
        data["series_id"] = series_id
    elif "series_id" not in data:
        raise ValueError("Missing series_id: 'series_id' argument not passed and column 'series_id' not present in dataframe") 
    if data.index.dtype.name != 'datetime64[ns, America/Argentina/Buenos_Aires]':
        if "timestart" in data.columns:
            data.index = data["timestart"].map(tryParseAndLocalizeDate)
        else:
            data.index = data.index.map(tryParseAndLocalizeDate)
    # raise Exception("index must be of type datetime64[ns, America/Argentina/Buenos_Aires]'")
    if column not in data.columns:
        raise Exception("column %s not found in data" % column)
    data = data.sort_index()
    if "timeend" in data:
        data["timeend"] = data["timeend"].map(tryParseAndLocalizeDate).map(lambda x: x.isoformat() if x is not None  and not pandas.isna(x) else None)
    else:
        data["timeend"] = data.index.map(lambda x: x.isoformat()) if timeSupport is None else data.index.map(lambda x: (x + timeSupport).isoformat())
    data["timestart"] = data.index.map(lambda x: x.isoformat()) # strftime('%Y-%m-%dT%H:%M:%SZ') 
    data["valor"] = data[column]
    data = data[["series_id","timestart","timeend","valor"]]
    return data.to_dict(orient="records")

def observacionTupleToDict(x : Union[Tuple[datetime,datetime,float], ObsTuple]) -> ObsTuple:
    if isinstance(x, tuple):
        return { 
            "timestart": x[0], 
            "valor": x[2]
        }
    elif isinstance(x, dict):
        return {
            "timestart": x["timestart"], 
            "valor": x["valor"]
        }
    else:
        raise TypeError("Invalid type")

def observacionesListToDataFrame(
    data: list, 
    tag: Optional[str] = None
    ) -> pandas.DataFrame:
    """Convert observaciones list to DataFrame

    Args:
        data (list): Observaciones
        tag (str, optional): String to set in tag column. Defaults to None.

    Raises:
        Exception: Empty list

    Returns:
        pandas.DataFrame: A DataFrame with datetime index and float column "valor". If tag was set, a "tag" column is added
    """
    if len(data) == 0:
        raise Exception("empty list")
    df : pandas.DataFrame = pandas.DataFrame(data)
    df["valor"] = df["valor"].astype(float)
    df.index = df["timestart"].apply(tryParseAndLocalizeDate)
    df.sort_index(inplace=True)
    if tag is not None:
        df["tag"] = tag
        return df[["valor","tag"]]
    else:
        return df[["valor",]]

def createEmptyObsDataFrame(
    extra_columns : Optional[dict] = None
    ) -> pandas.DataFrame:
    """Create Observations DataFrame with no rows

    Args:
        extra_columns (dict, optional): Additional columns. Keys are the column names, values are the column types. Defaults to None.

    Returns:
        pandas.DataFrame: Observations dataframe
    """
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
    return data[cnames]

def getSeriesTipo(series_table : Optional[SeriesTable] = None) -> Literal["puntual","areal","raster"]:
    if series_table is None:
        return "puntual"
    if series_table == "series":
        return "puntual"
    if series_table == "series_areal":
        return "areal"
    if series_table == "series_rast":
        return "raster"
    else:
        return "puntual"

def featureToSitio(
        feature : Feature
    ) -> Sitio:
    if "properties" not in feature:
        raise ValueError("Invalid GeoJSON: missing properties")
    if "geometry" not in feature:
        raise ValueError("Invalid GeoJSON: missing geomerty")
    if not "id" in feature["properties"]:
        raise ValueError("Invalid GeoJSON: missing property id")
    if not "nombre" in feature["properties"]:
        raise ValueError("Invalid GeoJSON: missing property nombre")
    id = int(feature["properties"]["id"])
    nombre = str(feature["properties"]["nombre"])
    sitio : Sitio = {
        "id": int(feature["properties"]["id"]),
        "nombre": str(feature["properties"]["nombre"]), 
        "geom": feature["geometry"]
    }
    return sitio

def geojsonToList(
        data : GeoJSON
    ) -> List[Sitio]:
    if "type" not in data:
        raise ValueError("Invalid GeoJSON: missing type")
    if data["type"] == "Feature":
        return [
            featureToSitio(data)
        ]
    else:
        if "features" not in data:
            raise ValueError("Invalid GeoJSON: missing features")
        return [
            featureToSitio(feature) for feature in data["features"]
        ]

def get_series_table(tipo: Optional[Literal["puntual","areal","raster"]]="puntual") -> Literal["series", "series_areal","series_rast"]:
    if tipo == "areal":
        return "series_areal"
    elif tipo == "raster":
        return "series_rast"
    else:
        return "series"

## EJEMPLO
'''
import pydrodelta.a5 as a5
import pydrodelta.util as util
# lee serie de api a5
serie = a5.readSerie(31532,"2022-05-25T03:00:00Z","2022-06-01T03:00:00Z")
serie2 = a5.readSerie(26286,"2022-05-01T03:00:00Z","2022-06-01T03:00:00Z")
# convierte observaciones a dataframe 
obs_df = a5.observacionesListToDataFrame(serie["observaciones"]) 
obs_df2 = a5.observacionesListToDataFrame(serie["observaciones"]) 
# crea index regular
new_index = util.createRegularDatetimeSequence(obs_df.index,timedelta(days=1))
# crea index regular a partir de timestart timeend
timestart = util.tryParseAndLocalizeDate("1989-10-14T03:00:00.000Z")
timeend = util.tryParseAndLocalizeDate("1990-03-10T03:00:00.000Z")
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