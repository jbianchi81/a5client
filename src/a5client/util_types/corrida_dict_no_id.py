from typing import TypedDict, List, Optional, NotRequired
from .series_prono_dict import SeriesPronoDict
from datetime import datetime

class CorridaDictNoId(TypedDict):
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
    forecast_date : datetime
    series: List[SeriesPronoDict]
