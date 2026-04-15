from unittest import TestCase, main
from datetime import datetime, date, timedelta
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
import pytz
from pytz.tzinfo import BaseTzInfo
from pytz.exceptions import NonExistentTimeError
from a5client.util import tryParseAndLocalizeDate, interval2relativedelta
from typing import cast
from a5client.util_types import IntervalDict

timezone = 'America/Argentina/Buenos_Aires'
tzone = pytz.timezone(timezone)

class TestParseDate(TestCase):
    def test_datetime(self):
        dt = datetime(1945,2,4,12)
        dt_parsed = tryParseAndLocalizeDate(dt)
        assert isinstance(dt_parsed, datetime)
        assert dt.timestamp() == dt_parsed.timestamp()
        assert dt_parsed.tzinfo is not None
        tzi = cast(BaseTzInfo, dt_parsed.tzinfo)
        assert tzi.zone == timezone

    def test_datetime_tz(self):
        dt = datetime(1945,2,4,12,tzinfo=tzone)
        dt_parsed = tryParseAndLocalizeDate(dt)
        assert isinstance(dt_parsed, datetime)
        assert dt.timestamp() == dt_parsed.timestamp()
        assert dt_parsed.tzinfo is not None
        tzi = cast(BaseTzInfo, dt_parsed.tzinfo)
        assert tzi.zone == timezone

    def test_date(self):
        dt = date(1945,2,4)
        dt_parsed = tryParseAndLocalizeDate(dt)
        assert isinstance(dt_parsed, datetime)
        assert dt == dt_parsed.date()
        assert dt_parsed.tzinfo is not None
        tzi = cast(BaseTzInfo, dt_parsed.tzinfo)
        assert tzi.zone == timezone

    def test_tuple(self):
        dt = (1945,2,4)
        dt_parsed = tryParseAndLocalizeDate(dt)
        assert isinstance(dt_parsed, datetime)
        assert dt_parsed.year == dt[0]
        assert dt_parsed.month == dt[1]
        assert dt_parsed.day == dt[2]
        assert dt_parsed.tzinfo is not None
        tzi = cast(BaseTzInfo, dt_parsed.tzinfo)
        assert tzi.zone == timezone

    def test_str(self):
        dt = "1945-02-04T15:00:00.000Z"
        dt_parsed = tryParseAndLocalizeDate(dt)
        assert isinstance(dt_parsed, datetime)
        assert dt_parsed.year == 1945
        assert dt_parsed.month == 2
        assert dt_parsed.day == 4
        assert dt_parsed.hour == 12
        assert dt_parsed.tzinfo is not None
        tzi = cast(BaseTzInfo, dt_parsed.tzinfo)
        assert tzi.zone == timezone

    def test_int(self):
        dt = 5
        t = datetime.now() + relativedelta(days=int(dt))
        dt_parsed = tryParseAndLocalizeDate(dt)
        assert isinstance(dt_parsed, datetime)
        assert dt_parsed.year == t.year
        assert dt_parsed.month == t.month
        assert dt_parsed.day == t.day
        assert dt_parsed.hour == t.hour
        assert dt_parsed.minute == t.minute
        assert dt_parsed.second == t.second
        assert dt_parsed.tzinfo is not None
        tzi = cast(BaseTzInfo, dt_parsed.tzinfo)
        assert tzi.zone == timezone

    def test_parse_interval_rd(self):
        interval = relativedelta(hours= 14)
        rd = interval2relativedelta(interval)
        assert isinstance(rd, relativedelta)
        assert interval == rd

    def test_parse_interval_td(self):
        interval = timedelta(hours= 14)
        rd = interval2relativedelta(interval)
        assert isinstance(rd, relativedelta)
        assert rd.hours == 14

    def test_parse_interval_dict(self):
        interval : IntervalDict = {"hours": 14}
        rd = interval2relativedelta(interval)
        assert isinstance(rd, relativedelta)
        assert rd.hours == 14

    def test_parse_interval_int(self):
        interval = 2
        rd = interval2relativedelta(interval)
        assert isinstance(rd, relativedelta)
        assert rd.days == 2
