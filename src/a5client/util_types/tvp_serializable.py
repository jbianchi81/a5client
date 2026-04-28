from typing import TypedDict, Optional

class TVPserializable(TypedDict):
    """
    Parameters:
    -----------
    timestart : datetime
    
    valor : float

    series_id : int = None
    """
    timestart : str
    valor : float
    series_id : Optional[int]
