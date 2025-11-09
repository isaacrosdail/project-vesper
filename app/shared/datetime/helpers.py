# Grabbing certain times / formatting datetimes

from datetime import datetime, time, timedelta, timezone, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def parse_js_instant(iso_str: str) -> datetime:
    """
    Parse a JS Date.toISOString() string into a timezone-aware UTC datetime.
    Intended for internal API calls from frontend.
    Must end in 'Z'. Example: "2025-08-21T03:14:15.123Z"
    """
    if not iso_str.endswith("Z"):
        raise ValueError(f"Expected UTC instant ending with 'Z', got: {iso_str}")
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))


def now_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(ZoneInfo("UTC"))


def now_in_timezone(tz_str: str) -> datetime:
    """Return the current datetime in the given timezone."""
    try:
        tz = ZoneInfo(tz_str)
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone: {tz_str}")
    return datetime.now(tz)


def convert_to_timezone(tz_str: str, dt: datetime) -> datetime:
    """Convert a timezone-aware datetime to the given timezone."""
    if dt.tzinfo is None:
        raise ValueError("Naive datetimes not allowed")
    try:
        tz = ZoneInfo(tz_str)
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone: {tz_str}")
    return dt.astimezone(tz)


def day_range_utc(date: date, tz_str: str) -> tuple[datetime, datetime]:
    """Return (start, end) UTC bounds of the given *calendar day* in the specified timezone. Interval is [start, end)"""
    tz = ZoneInfo(tz_str)
    # Extract date, make midnight in target timezone
    start_local = datetime.combine(date, time.min, tzinfo=tz)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=1) # end is midnight
    return start_utc, end_utc


def today_range_utc(tz_str: str) -> tuple[datetime, datetime]:
    """Return (start, end) UTC bounds for today in the specified timezone. Interval is [start, end)"""
    return day_range_utc(datetime.now(ZoneInfo(tz_str)).date(), tz_str)


def last_n_days_range(days_ago: int, tz_str: str) -> tuple[datetime, datetime]:
    """
    Return (start_utc, end_utc) for last N days including today in user's timezone.

    EX: days_ago=7 in London timezone.
    - Today is Dec 15th in London
    - Returns: (Dec 9th 00:00 London -> UTC, Dec 15th 23:59 London -> UTC)
    """
    start_utc, end_utc = today_range_utc(tz_str)

    # Go back (days_ago - 1) to incl. today as 'day #1'
    new_start_utc = start_utc - timedelta(days=(days_ago - 1))
    return new_start_utc, end_utc


def parse_time_to_datetime(time_str: str, date: date, tz_str: str) -> datetime:
    """Parse HH:MM and attach to specific date in given timezone."""
    h, m = map(int, time_str.split(":"))
    tz = ZoneInfo(tz_str)
    return datetime(date.year, date.month, date.day, h, m, tzinfo=tz)


def is_same_local_date(dt: datetime, tz_str: str) -> bool:
    """Return True if given datetime occurs on the same calendar date as 'now' in user's timezone."""
    local_dt = dt.astimezone(ZoneInfo(tz_str))
    today_local = now_utc().astimezone(ZoneInfo(tz_str)).date()
    return local_dt.date() == today_local