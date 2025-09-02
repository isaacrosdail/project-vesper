from app.shared.datetime.helpers import parse_js_instant, convert_to_timezone, day_range, today_range, last_n_days_range
from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo
import pytest
from unittest.mock import patch

# Verify: Happy path, MS optional, ?
@pytest.mark.parametrize("iso_str, expected", [
    ("2025-08-21T03:14:15.123Z", datetime(2025, 8, 21, 3, 14, 15, 123000, tzinfo=timezone.utc)),
    ("2025-08-21T03:14:15Z", datetime(2025, 8, 21, 3, 14, 15, tzinfo=timezone.utc)),
    ("2025-08-21T03:14:15+00:00", datetime(2025, 8, 21, 3, 14, 15, tzinfo=timezone.utc)),
])
def test_parse_js_instant_success_cases(iso_str, expected):
    result = parse_js_instant(iso_str)
    assert result == expected

def test_parse_js_instant_invalid_format_raises():
    with pytest.raises(ValueError):
        parse_js_instant("not-a-date")

def test_convert_to_timezone_converts_utc_to_local_timezone():
    utc_dt = datetime(2025, 7, 15, 14, 30, tzinfo=timezone.utc)
    result = convert_to_timezone("America/New_York", utc_dt)

    # EDT in July = UTC-4 so 14:30 UTC => 10:30 EDT
    assert result.hour == 10
    assert result.minute == 30
    assert str(result.tzinfo) == "America/New_York"

def test_convert_to_timezone_invalid_timezone_raises():
    with pytest.raises(ValueError, match="Invalid timezone"):
        convert_to_timezone("My/FakeZone")



def test_day_range_new_york_user():
    # NY user wants data for March 15th
    march_15 = date(2025, 3, 15)
    start_utc, end_utc = day_range(march_15, "America/New_York")

    # March 15th is during EDT (UTC-4)
    # "March 15 0:00 EDT" = "March 15 04:00 UTC"
    # "March 16 0:00 EDT" = "March 16 04:00 UTC"
    expected_start = datetime(2025, 3, 15, 4, 0, tzinfo=timezone.utc)
    expected_end = datetime(2025, 3, 16, 4, 0, tzinfo=timezone.utc)

    assert start_utc == expected_start
    assert end_utc == expected_end

def test_day_range_during_dst_transition():
    # Spring forward day in 2025: March 9th
    # 2 AM becomes 3 AM, so this day is only 23 hours long
    march_9 = date(2025, 3, 9)
    start_utc, end_utc = day_range(march_9, "America/New_York")
    
    # Should still be a 24-hour UTC span even though the local day is 23 hours
    duration = end_utc - start_utc
    assert duration == timedelta(days=1)  # 24 hours in UTC

def test_day_range_fall_back_dst():
    # Fall back day in 2025: November 2nd
    # 2 AM becomes 1 AM, so this day is 25 hours long locally
    nov_2 = date(2025, 11, 2)
    start_utc, end_utc = day_range(nov_2, "America/New_York")
    
    # Should still be 24 UTC hours even though local day is 25 hours
    duration = end_utc - start_utc
    assert duration == timedelta(days=1)

def test_today_range_ny_with_mocked_now():
    mock_now = datetime(2025, 8, 25, 12, 34, 56, tzinfo=timezone.utc)

    with patch("app.shared.datetime.helpers.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine  # needed because combine is used
        mock_datetime.timezone = timezone         # keep reference to timezone

        start_utc, end_utc = today_range("America/New_York")

    assert start_utc.isoformat() == "2025-08-25T04:00:00+00:00"
    assert end_utc.isoformat()   == "2025-08-26T04:00:00+00:00"


def test_last_n_days_range_ny_with_mocked_now():
    mock_now = datetime(2025, 8, 25, 12, 0, 0, tzinfo=timezone.utc)

    with patch("app.shared.datetime.helpers.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.timezone = timezone
        mock_datetime.timedelta = timedelta

        start_utc, end_utc = last_n_days_range(7, "America/New_York")

    assert start_utc.isoformat() == "2025-08-19T04:00:00+00:00"
    assert end_utc.isoformat()   == "2025-08-26T04:00:00+00:00"
