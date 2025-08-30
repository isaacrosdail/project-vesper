
from datetime import datetime, timedelta
from app.shared.datetime.helpers import convert_to_timezone

# Parse HH:MM for started_at from form field & anchor to today in user's timezone
def resolve_start(time_str: str, tz_str: str) -> datetime:
    h, m = map(int, time_str.split(":"))
    now = convert_to_timezone(tz_str)
    return now.replace(hour=h, minute=m, second=0, microsecond=0)

def resolve_end(started_at: datetime, duration: float) -> datetime:
    return started_at + timedelta(minutes=duration)