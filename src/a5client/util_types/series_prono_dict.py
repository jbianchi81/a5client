from typing import TypedDict, List, Optional, Literal, Union, NotRequired
from .tvp_prono import TVPProno
from datetime import datetime

class SeriesPronoDict(TypedDict):
    """
    Parameters:
    -----------
    series_id : int
    
    series_table : str
    
    pronosticos: List[TVP]
    """
    series_id : int
    series_table : Literal["series","series_areal","series_rast"]
    pronosticos: List[TVPProno]
    cal_id : NotRequired[Optional[int]]
    tipo : NotRequired[Optional[Literal["puntual","areal","raster"]]]
    qualifier : Optional[str]
    qualifiers : Optional[List[str]]
    forecast_timestart : NotRequired[Optional[datetime]]
    forecast_timeend : NotRequired[Optional[datetime]]
    forecast_date : NotRequired[Optional[datetime]]
    cor_id : NotRequired[Optional[int]]
    var_id : NotRequired[Optional[int]]
    begin_date : NotRequired[Optional[datetime]]
    end_date : NotRequired[Optional[datetime]]
    qualifiers : NotRequired[Optional[List[str]]]
    count : NotRequired[Optional[int]]
    estacion_id : NotRequired[Optional[int]]
