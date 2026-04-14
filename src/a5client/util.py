from datetime import datetime, timedelta, date as datetime_date
from typing import Union, Optional, TypedDict, Literal, overload, cast
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from dateutil import tz
import pytz
from pytz.exceptions import NonExistentTimeError
import logging
from pandas import DatetimeIndex, date_range, DateOffset
from .util_types import Dateable

class IntervalDict(TypedDict):
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


@overload
def tryParseAndLocalizeDate(
        date_ : Dateable,
        timezone : str='America/Argentina/Buenos_Aires',
        *,
        allow_nonexistent : Literal[True]
    ) -> Optional[datetime]: ...
@overload
def tryParseAndLocalizeDate(
        date_ : Dateable,
        timezone : str='America/Argentina/Buenos_Aires',
        *,
        allow_nonexistent : Literal[False] = False
    ) -> datetime: ...
def tryParseAndLocalizeDate(
        date_ : Dateable,
        timezone : str='America/Argentina/Buenos_Aires',
        *,
        allow_nonexistent : bool=False
    ) -> Optional[datetime]:
    """
    Datetime parser. If duration is provided, computes date relative to now.

    Parameters:
    -----------
    date_string : str or float or datetime.datetime
        For absolute date: ISO-8601 datetime string or datetime.datetime or (year,month,date) tuple.
        For relative date: dict (duration key-values) or float (decimal number of days)
    
    timezone : str
        Time zone string identifier. Default: America/Argentina/Buenos_Aires
    
    Returns:
    --------
    datetime.datetime

    Examples:
    ---------
    ``` 
    tryParseAndLocalizeDate("2024-01-01T03:00:00.000Z")
    tryParseAndLocalizeDate(1.5)
    tryParseAndLocalizeDate({"days":1, "hours": 12}, timezone = "Africa/Casablanca")
    tryParseAndLocalizeDate((2000,1,1))
    ```
    """
    
    if isinstance(date_, str):
        date = isoparse(date_)
    elif isinstance(date_,dict):
        date = cast(datetime, datetime.now() + relativedelta(**date_))
    elif isinstance(date_,(int,float)):
        date = cast(datetime, datetime.now() + relativedelta(days=int(date_)))
    elif isinstance(date_, tuple):
        if len(date_) < 3:
            raise ValueError("Invalid date tuple: missing items (3 required)")
        date = datetime(*date_)
    elif isinstance(date_, datetime):
        date = date_
    elif isinstance(date_, datetime_date):
        date = datetime(date_.year, date_.month, date_.day)
    else:
        raise TypeError(f"invalid type ${type(date_)} for datetime parsing")
        
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        try:
            tzone = pytz.timezone(timezone)
            date = cast(datetime, tzone.localize(date))
            # date = date.replace(tzinfo = pytz.timezone(timezone)) # ZoneInfo(timezone))
        except NonExistentTimeError as e:
            if allow_nonexistent:
                logging.warning("NonexistentTimeError: %s" % str(date))
                return None
            raise e
    else:
        date = date.astimezone(pytz.timezone(timezone)) # ZoneInfo(timezone))
    return date

def createDatetimeSequence(
    datetime_index : Optional[DatetimeIndex]=None, 
    timeInterval : Union[relativedelta,dict,int,timedelta] = relativedelta(days=1), 
    timestart : Union[datetime,tuple,str,None] = None, 
    timeend : Union[datetime,tuple,str,None] = None, 
    timeOffset : Union[relativedelta,dict,None] = None
    ) -> DatetimeIndex:
    #Fechas desde timestart a timeend con un paso de timeInterval
    #data: dataframe con index tipo datetime64[ns, America/Argentina/Buenos_Aires]
    #timeOffset sólo para timeInterval n days
    if timestart is None:
        if datetime_index is None:
            raise Exception("Missing datetime_index or timestart+timeend")
        timestart = datetime_index.min()
    else:
        timestart = tryParseAndLocalizeDate(timestart)
    if timestart is None:
        raise pytz.exceptions.NonExistentTimeError("Nonexistent timestart")
    if timeend is None:
        if datetime_index is None:
            raise Exception("Missing datetime_index or timestart+timeend")
        timeend = datetime_index.max()
    else:
        timeend = tryParseAndLocalizeDate(timeend)
    if timeend is None:
        raise pytz.exceptions.NonExistentTimeError("Nonexistent timeend")
    timeInterval = relativedelta(**timeInterval) if isinstance(timeInterval,dict) else timedelta_to_relativedelta(timeInterval) if isinstance(timeInterval,timedelta) else relativedelta(days=timeInterval) if isinstance(timeInterval, int) else timeInterval
    timeOffset = relativedelta(**timeOffset) if isinstance(timeOffset,dict) else timeOffset
    timestart = roundDate(timestart,timeInterval,timeOffset,"up")
    timeend = roundDate(timeend,timeInterval,timeOffset,"down")
    timezone = pytz.timezone("America/Argentina/Buenos_Aires")
    is_subdaily = timeInterval.hours > 0 or timeInterval.minutes > 0 or timeInterval.seconds > 0 or timeInterval.microseconds > 0
    if not is_subdaily:
        if timestart.day == 1 and timeInterval.months > 0:
            freq = "%iMS" % timeInterval.months
        elif timestart.day == 1 and timestart.month == 1 and timeInterval.years > 0:
            freq = "%iYS" % timeInterval.years 
        elif timeInterval.days > 0:
            freq = "%iD" % timeInterval.days
        else:
            freq = relativedelta_to_freq(timeInterval)
        dts_utc = date_range(
            start=timestart.astimezone(tz.UTC), 
            end=timeend.astimezone(tz.UTC), 
            freq = freq
        )
        if timeOffset is not None:
            return DatetimeIndex([timezone.localize(datetime(dt.year,dt.month,dt.day,timeOffset.hours,timeOffset.minutes,timeOffset.seconds)) for dt in dts_utc])
        else:
            return DatetimeIndex([timezone.localize(datetime(dt.year,dt.month,dt.day)) for dt in dts_utc])
    else:
        freq = DateOffset(
                years=timeInterval.years,
                months=timeInterval.months,
                weeks=timeInterval.weeks,
                days=timeInterval.days, 
                hours=timeInterval.hours, 
                minutes = timeInterval.minutes,
                seconds = timeInterval.seconds,
                microseconds = timeInterval.microseconds
            )
        return date_range(
            start=timestart, 
            end=timeend, 
            freq=freq
        ) # .tz_convert(timestart.tzinfo)

def roundDate(date : datetime,timeInterval : relativedelta,timeOffset : Optional[relativedelta]=None, to="up") -> datetime:
    date_0 = tryParseAndLocalizeDate(datetime.combine(date.date(),datetime.min.time()))
    if date_0 is None:
        raise NonExistentTimeError("Nonexistent time")
    if timeOffset is not None:
        date_0 = date_0 + timeOffset 
    while date_0 < date:
        date_0 = date_0 + timeInterval
    if date_0 == date:
        return date_0
    elif to == "up":
        return date_0
    else:
        return date_0 - timeInterval

def interval2timedelta(interval : Union[dict,float,timedelta]):
    """Parses duration dict or number of days into datetime.timedelta object
    
    Parameters:
    -----------
    interval : dict or float (decimal number of days) or datetime.timedelta
        If dict, allowed keys are:
        - days
        - seconds
        - microseconds
        - minutes
        - hours
        - weeks
    
    Returns:
    --------
    duration : datetime.timedelta

    Examples:

    ```
    interval2timedelta({"hours":1, "minutes": 30})
    interval2timedelta(1.5/24)
    ```
    """
    if isinstance(interval,timedelta):
        return interval
    if isinstance(interval,(float,int)):
        return timedelta(days=interval)
    days = 0
    seconds = 0
    microseconds = 0
    milliseconds = 0
    minutes = 0
    hours = 0
    weeks = 0
    for k in interval:
        if k == "milliseconds" or k == "millisecond":
            milliseconds = interval[k]
        elif k == "seconds" or k == "second":
            seconds = interval[k]
        elif k == "minutes" or k == "minute":
            minutes = interval[k]
        elif k == "hours" or k == "hour":
            hours = interval[k]
        elif k == "days" or k == "day":
            days = interval[k]
        elif k == "weeks" or k == "week":
            weeks = interval[k] * 86400 * 7
    return timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

def timedelta_to_relativedelta(td: timedelta) -> relativedelta:
    total_seconds = td.total_seconds()
    
    days, remainder = divmod(total_seconds, 86400)  # seconds in a day
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return relativedelta(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds)
    )

def relativedelta_to_timedelta(rd: relativedelta) -> timedelta:
    if not isinstance(rd, relativedelta):
        raise TypeError("Value must be of type relativedelta")
    total_seconds = relativedeltaToSeconds(rd)
    days, remainder = divmod(total_seconds, 86400)  # seconds in a day
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return timedelta(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds)
    )

def relativedeltaToSeconds(rd : relativedelta) -> int:
    if not isinstance(rd, relativedelta):
        raise TypeError("Value must be of type relativedelta")
    now = datetime.now()
    future = now + rd
    delta = future - now
    return int(delta.total_seconds())

def relativedelta_to_freq(rd: relativedelta) -> str:
    if rd.years:
        return f"{rd.years}Y"
    if rd.months:
        return f"{rd.months}M"
    if rd.days:
        return f"{rd.days}D"
    if rd.hours:
        return f"{rd.hours}H"
    if rd.minutes:
        return f"{rd.minutes}T"
    if rd.seconds:
        return f"{rd.seconds}S"
    raise ValueError("Unsupported relativedelta")
