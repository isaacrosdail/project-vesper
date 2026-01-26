from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
import time_machine

from app.shared.datetime_.helpers import *


@pytest.mark.parametrize("iso_str, expected_datetime", [
    (
        "2025-08-21T03:14:15.123Z",
        datetime(2025, 8, 21, 3, 14, 15, 123000, tzinfo=ZoneInfo("UTC"))
    ),
    (
        "2025-08-21T03:14:15Z",
        datetime(2025, 8, 21, 3, 14, 15, tzinfo=ZoneInfo("UTC"))
    ),
])
def test_parse_js_instant_success_cases(iso_str, expected_datetime):
    result = parse_js_instant(iso_str)
    assert result == expected_datetime

@pytest.mark.parametrize("iso_str", [
    "2025-08-21T03:14:15+00:00",  # wrong format
    "2025-08-21T03:14:15",        # naive datetime
    "2025-08-21T03:14:15+02:00",  # non-UTC
    "not-a-date",                 # nonsense
])
def test_parse_js_instant_failure(iso_str):
    with pytest.raises(ValueError):
        parse_js_instant(iso_str)


def test_convert_to_timezone_valid():
    dt = datetime(2025, 9, 30, 12, 0, tzinfo=ZoneInfo("UTC"))
    result = convert_to_timezone("America/New_York", dt)
    assert result.tzinfo == ZoneInfo("America/New_York")


@pytest.mark.parametrize("date, tz_str, expected_start, expected_end", [
    (
        datetime(2025, 9, 30),
        "UTC",
        datetime(2025, 9, 30, 0, 0, tzinfo=ZoneInfo("UTC")),
        datetime(2025, 10, 1, 0, 0, tzinfo=ZoneInfo("UTC"))
    ),
    (
        datetime(2025, 9, 30),
        "America/New_York",
        datetime(2025, 9, 30, 4, 0, tzinfo=ZoneInfo("UTC")),
        datetime(2025, 10, 1, 4, 0, tzinfo=ZoneInfo("UTC"))
    ),
])
def test_day_range_utc(date, tz_str, expected_start, expected_end):
    start_utc, end_utc = day_range_utc(date, tz_str)
    assert start_utc == expected_start
    assert end_utc == expected_end



@pytest.mark.parametrize("tz_str, expected_start, expected_end", [
    ("UTC",
     datetime(2025, 9, 29, 0, 0, tzinfo=ZoneInfo("UTC")),
     datetime(2025, 9, 30, 0, 0, tzinfo=ZoneInfo("UTC"))),

    ("America/New_York",
     datetime(2025, 9, 29, 4, 0, tzinfo=ZoneInfo("UTC")),
     datetime(2025, 9, 30, 4, 0, tzinfo=ZoneInfo("UTC"))),
])
@time_machine.travel(datetime(2025, 9, 29, 10, 0, tzinfo=ZoneInfo("UTC")), tick=False)
def test_today_range_utc(tz_str, expected_start, expected_end):
    start, end = today_range_utc(tz_str)
    assert start == expected_start
    assert end == expected_end


# TODO: last_n_days_range
@pytest.mark.parametrize("days_ago, tz_str, expected_start_utc, expected_end_utc", [
    pytest.param(7, "UTC",
     datetime(2025, 9, 23, 0, 0, tzinfo=ZoneInfo("UTC")),
     datetime(2025, 9, 30, 0, 0, tzinfo=ZoneInfo("UTC")),
     id="utc"
     ),
     pytest.param(7, "America/Chicago",
      datetime(2025, 9, 23, 5, 0, tzinfo=ZoneInfo("UTC")),
      datetime(2025, 9, 30, 5, 0, tzinfo=ZoneInfo("UTC")),
      id="chicago-offset"
      ),
])
@time_machine.travel(datetime(2025, 9, 29, 10, 0, tzinfo=ZoneInfo("UTC")), tick=False)
def test_last_n_days_range(days_ago, tz_str, expected_start_utc, expected_end_utc):
    start_utc, end_utc = last_n_days_range(days_ago, tz_str)
    assert start_utc == expected_start_utc
    assert end_utc == expected_end_utc


# TODO: parse_time_to_datetime
@pytest.mark.parametrize("time_str, date, tz_str, expected_datetime", [
    (
        "14:30", 
        date(2025, 9, 29),
        "America/Chicago",
        datetime(2025, 9, 29, 14, 30, tzinfo=ZoneInfo("America/Chicago"))
     ),
     (
         "00:00",
         date(2025, 9, 29),
         "UTC",
         datetime(2025, 9, 29, 0, 0, tzinfo=ZoneInfo("UTC"))
     ),
])
def test_parse_time_to_datetime(time_str, date, tz_str, expected_datetime):
    dt = parse_time_to_datetime(time_str, date, tz_str)
    assert dt == expected_datetime