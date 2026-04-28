# from typing import TypedDict
from .interval_dict import IntervalDict

class A5IntervalDict(IntervalDict, total=False):
    years : int
    months : int
    days : int
    hours : int
    minutes : int
    seconds : int
    milliseconds : int
