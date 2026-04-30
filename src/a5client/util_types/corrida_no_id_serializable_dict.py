from typing import TypedDict, List, Optional
from typing_extensions import NotRequired
from .series_prono_serializable_dict import SeriesPronoSerializableDict
from datetime import datetime

class CorridaNoIdSerializableDict(TypedDict):
    """
    Parameters:
    -----------
    cal_id : int
    
    id : Optional[int]

    forecast_date : datetime
    
    series: List[SeriesPronoDict]
    """
    cal_id : int
    id : NotRequired[Optional[int]]
    forecast_date : str
    series: List[SeriesPronoSerializableDict]
