from typing import Optional, NotRequired, TypedDict

class TVPPronoSerializable(TypedDict):
    timestart : str
    timeend : NotRequired[Optional[str]]
    valor : float
    series_id : NotRequired[Optional[int]]
    qualifier : NotRequired[Optional[str]]