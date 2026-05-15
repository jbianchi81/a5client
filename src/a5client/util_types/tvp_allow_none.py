from typing import TypedDict, Optional
from typing_extensions import NotRequired
from datetime import datetime

class TVPAllowNone(TypedDict):
    """
    Parameters:
    -----------
    timestart : datetime
    
    valor : float

    series_id : int = None
    """
    timestart : datetime
    timeend : NotRequired[Optional[datetime]]
    valor : Optional[float]
    series_id : NotRequired[Optional[int]]
