# Grabbing certain times / formatting datetimes

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def now_utc():
    return datetime.now(timezone.utc)

def now_local(timezone_str: str = 'UTC') -> datetime:
    """
    Get current time in specified timezone.
    
    Args:
        timezone_str: Timezone string (eg, 'US/Central', 'UTC')
    Returns:
        Timezone-aware datetime object
    """
    try:
        # Make tz object
        tz = ZoneInfo(timezone_str)
        return datetime.now(tz) # current time in that timezone
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone: {timezone_str}")