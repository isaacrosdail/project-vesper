# Grabbing certain times / formatting datetimes

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def parse_js_instant(iso_str: str) -> datetime:
    """
    Parse a JS Date.toISOString() string into a timezone-aware UTC datetime.
    Intended for internal API calls from frontend.
    Example input: "2025-08-21T03:14:15.123Z"
    """
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def datetime_local(tz_str: str = 'UTC', dt: datetime | None = None) -> datetime:
    """
    Return a timezone-aware datetime in the given timezone.

    Behavior:
        - If dt is provided: Convert dt to the specified timezone.
        - If dt is not provided: Return the current time ("now") in the specified timezone.
    """
    try:
        tz = ZoneInfo(tz_str)       # make tz object, behaves like full IANA timezone (handles DST transitions)
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone: {tz_str}")
    
    if dt is not None:
        return dt.astimezone(tz) # convert provided
    else:
        return datetime.now(tz)  # or return 'now' if none provided

    

def start_of_day_utc(dt: datetime, tz: str = "UTC") -> datetime:
    """Get start of day in UTC for a given datetime in given timezone."""
    zone = ZoneInfo(tz)
    start_local = datetime.combine(dt.date(), time.min, tzinfo=zone)
    return start_local.astimezone(timezone.utc)

def today_range(tz_str: str = "UTC") -> tuple[datetime, datetime]:
    """
    Return (start_of_day_utc, end_of_day_utc) for today in given timezone.
    Helpful for our "Did it happen today?" queries.
    """
    now = datetime_local(tz_str)
    start_utc = start_of_day_utc(now, tz_str)
    end_utc = (start_utc + timedelta(days=1))
    return start_utc, end_utc

def day_range(date: datetime.date, tz_str: str = "UTC") -> tuple[datetime, datetime]:
    """
    Return (start_utc, end_utc) bounds in UTC for a given date (no time) in a user's timezone.
    """
    dt = datetime.combine(date, time.min)
    start_utc = start_of_day_utc(dt, tz_str)
    end_utc = (start_utc + timedelta(days=1))
    return start_utc, end_utc

def last_n_days_range(days_ago: int, tz_str: str = "UTC") -> tuple[datetime, datetime]:
    """
    Return (start_utc, end_utc) for last N days including today in user's timezone.

    EX: days_ago=7 in London timezone.
    - Today is Dec 15th in London
    - Returns: (Dec 9th 00:00 London -> UTC, Dec 15th 23:59 London -> UTC)
    """
    start_utc, end_utc = today_range(tz_str)

    # Go back (days_ago - 1) to incl. today as 'day #1'
    new_start_utc = start_utc - timedelta(days=(days_ago - 1))
    return new_start_utc, end_utc