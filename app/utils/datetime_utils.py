from datetime import datetime, timezone
import pytz

def now_utc():
    return datetime.now(timezone.utc)

def parse_local_datetime_to_utc(dt_str: str, local_tz_str: str = "America/Chicago"):
    local_tz = pytz.timezone(local_tz_str)
    naive = datetime.strptime(dt_str, "%Y-%m-%d")
    local_dt = local_tz.localize(naive)
    return local_dt.astimezone(timezone.utc)

