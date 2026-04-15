from datetime import timedelta
from dateutil.relativedelta import relativedelta
from typing import Union
from .interval_dict import IntervalDict

Intervaleable = Union[relativedelta, timedelta, IntervalDict, int]