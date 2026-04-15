from typing import TypedDict

class IntervalDict(TypedDict, total=False):
    day: int
    second : int
    microsecond : int
    minute : int
    hour : int
    month: int
    days: int
    seconds : int
    microseconds : int
    minutes : int
    hours : int
    weeks : int
    months: int

