from typing import TypedDict, Optional
from typing_extensions import NotRequired

class TVPserializable(TypedDict):
    """
    Parameters:
    -----------
    timestart : datetime
    
    valor : float

    series_id : int = None
    """
    timestart : str
    timeend : NotRequired[Optional[str]]
    valor : float
    series_id : Optional[int]
