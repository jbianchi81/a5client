from typing import TypedDict, List, Literal
from .tvp import TVP

class SeriesDict(TypedDict):
    """
    Parameters:
    -----------
    series_id : int
    
    series_table : str
    
    observaciones: List[TVP]
    """
    series_id : int
    series_table : Literal["series","series_areal","series_rast"]
    observaciones: List[TVP]
