from typing import TypedDict, Optional, NotRequired
from datetime import datetime
from .dateable import Dateable

class TVPdateable(TypedDict):
    """
    Parameters:
    -----------
    timestart : datetime
    
    valor : float

    series_id : int = None
    """
    timestart : Dateable
    timeend : NotRequired[Optional[Dateable]]
    valor : float
    series_id : NotRequired[Optional[int]]
