from typing import Optional, NotRequired, TypedDict
from datetime import datetime

class TVPProno(TypedDict):
    timestart : datetime
    timeend : NotRequired[Optional[datetime]]
    valor : float
    series_id : NotRequired[Optional[int]]
    qualifier : NotRequired[Optional[str]]