from typing import Optional, TypedDict
from typing_extensions import NotRequired

class TVPPronoSerializable(TypedDict):
    timestart : str
    timeend : NotRequired[Optional[str]]
    valor : float
    series_id : NotRequired[Optional[int]]
    qualifier : NotRequired[Optional[str]]