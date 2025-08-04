# Helper functions for handling conversion to/from UTC

from datetime import datetime, timezone
from zoneinfo import \
    ZoneInfo  # new gold standard for timezone lib in Python? dbl check


def utc_to_local(utc_time: datetime, user_timezone: str) -> datetime:
    pass

def parse_local_to_utc(dt_str: str, format: str = "%Y-%m-%d", timezone_str: str = "America/Chicago") -> datetime:
    """Parse string as local time and convert to UTC datetime object."""
    naive = datetime.strptime(dt_str, format)
    local_dt = naive.replace(tzinfo=ZoneInfo(timezone_str))
    return local_dt.astimezone(timezone.utc)

