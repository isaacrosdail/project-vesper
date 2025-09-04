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

def convert_to_timezone(tz_str: str = 'UTC', dt: datetime | None = None) -> datetime:
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
        return dt.astimezone(tz)
    else:
        return datetime.now(tz)

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
    # Get current time in user's time
    tz = ZoneInfo(tz_str)
    now_local = datetime.now(tz)

    # Calculate start of today in user's timezone, convert to UTC
    start_local = datetime.combine(now_local.date(), time.min, tzinfo=tz)
    start_utc = start_local.astimezone(timezone.utc)

    # End is start of tomorrow
    end_utc = start_utc + timedelta(days=1)
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


def parse_eod_datetime_from_date(date_str: str, tz_str: str) -> datetime:
    eod_time = time(23, 59, 59)
    tz = ZoneInfo(tz_str)
    eod_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    eod_datetime = datetime.combine(eod_date, eod_time)
    eod_datetime_aware = eod_datetime.replace(tzinfo=tz)

    return eod_datetime_aware


def parse_datetime_from_hhmm(time_str: str, tz_str: str) -> datetime:
    """Parse HH:MM format in given timezone and return proper datetime object."""
    h, m = map(int, time_str.split(":"))
    now = convert_to_timezone(tz_str)
    return now.replace(hour=h, minute=m, second=0, microsecond=0)

def add_mins_to_datetime(started_at: datetime, duration: float) -> datetime:
    """Return an end datetime from a start time & duration in minutes."""
    return started_at + timedelta(minutes=duration)