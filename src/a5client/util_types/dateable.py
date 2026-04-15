from datetime import datetime, date
from typing import Union
from .interval_dict import IntervalDict

Dateable = Union[datetime, date, tuple, str, int, IntervalDict]
"""Union[datetime, date, tuple, str, int]"""