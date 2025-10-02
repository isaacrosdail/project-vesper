from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
import time_machine

from app.shared.datetime.helpers import *


@pytest.mark.parametrize("iso_str, expected", [
    ("2025-08-21T03:14:15.123Z", datetime(2025, 8, 21, 3, 14, 15, 123000, tzinfo=ZoneInfo("UTC"))),
    ("2025-08-21T03:14:15Z", datetime(2025, 8, 21, 3, 14, 15, tzinfo=ZoneInfo("UTC"))),
])
def test_parse_js_instant_success_cases(iso_str, expected):
    result = parse_js_instant(iso_str)
    assert result == expected

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


# start_of_day_utc
@pytest.mark.parametrize("dt, tz_str, expected", [
    # UTC midnight stays midnight UTC
    (datetime(2025, 9, 30, 15, 0, tzinfo=timezone.utc), "UTC",
     datetime(2025, 9, 30, 0, 0, tzinfo=timezone.utc)),

    # New York midnight = 4am UTC (Sept 30 2025, no DST shift)
    (datetime(2025, 9, 30, 12, 0, tzinfo=ZoneInfo("America/New_York")), "America/New_York",
     datetime(2025, 9, 30, 4, 0, tzinfo=timezone.utc)),
])
def test_start_of_day_utc(dt, tz_str, expected):
    result, _ = day_range_utc(dt, tz_str)
    assert result == expected


def test_start_of_day_utc_rejects_naive():
    from datetime import datetime
    with pytest.raises(ValueError):
        day_range_utc(datetime(2025, 9, 30, 12, 0), "UTC")


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

