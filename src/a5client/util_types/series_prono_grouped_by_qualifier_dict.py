from typing import TypedDict, List, Optional, Literal, Union
from .tvp_grouped_by_qualifier import TVPGroupedByQualifier
from datetime import datetime

class SeriesPronoGroupedByQualifierDict(TypedDict):
    """
    Parameters:
    -----------
    series_id : int
    
    series_table : str
    
    pronosticos: List[TVP]
    """
    series_id : int
    series_table : str
    pronosticos: List[TVPGroupedByQualifier]
    cal_id : Optional[int]
    tipo : Optional[Literal["puntual","areal","raster"]]
    forecast_timestart : Optional[datetime]
    forecast_timeend : Optional[datetime]
    forecast_date : Optional[datetime]
