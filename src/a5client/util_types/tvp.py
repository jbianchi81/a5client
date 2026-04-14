from typing import TypedDict, Optional, NotRequired
from datetime import datetime

class TVP(TypedDict):
    """
    Parameters:
    -----------
    timestart : datetime
    
    valor : float

    series_id : int = None
    """
    timestart : datetime
    timeend : NotRequired[Optional[datetime]]
    valor : float
    series_id : int
