from typing import TypedDict, List, Literal
from .tvp_serializable import TVPserializable

class SeriesSerializableDict(TypedDict):
    """
    Parameters:
    -----------
    series_id : int
    
    series_table : str
    
    observaciones: List[TVP]
    """
    series_id : int
    series_table : Literal["series","series_areal","series_rast"]
    observaciones: List[TVPserializable]
