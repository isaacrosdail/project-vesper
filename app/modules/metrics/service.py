from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.constants import WAKE_MUST_BE_AFTER_SLEEP
from app.shared.datetime.helpers import today_range_utc, parse_time_to_datetime
from app.api.responses import service_response


class DailyMetricsService:
    def __init__(self, repository: DailyMetricsRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def save_daily_entry(self, typed_data: dict, entry_id: int | None) -> dict:

        # Check wake/sleep times are sensible
        if "wake_time" in typed_data and "sleep_time" in typed_data:
            wake_dt = self._convert_time_to_datetime("wake_time", typed_data["wake_time"])
            sleep_dt = self._convert_time_to_datetime("sleep_time", typed_data["sleep_time"])

            if wake_dt <= sleep_dt:
                return service_response(
                    False,
                    "Wake/Sleep time check failed",
                    errors={
                        "wake_time": [WAKE_MUST_BE_AFTER_SLEEP],
                        "sleep_time": [WAKE_MUST_BE_AFTER_SLEEP]
                    }
                )

        # UPDATE
        if entry_id is not None:
            entry = self.repo.get_daily_metric_by_id(entry_id)
            if not entry:
                return service_response(False, "Daily entry not found")
            
            for field, value in typed_data.items():
                if field in ("wake_time", "sleep_time"):
                    value = self._convert_time_to_datetime(field, value)
                setattr(entry, field, value)
    
            return service_response(True, "Daily entry updated", data={"entry": entry})
    
        # CREATE/UPSERT (for today)
        for field, value in typed_data.items():
            if field in ("wake_time", "sleep_time"):
                value = self._convert_time_to_datetime(field, value)
            
            start_utc, end_utc = today_range_utc(self.user_tz)
            entry, was_created = self.repo.create_or_update_daily_metric(
                field, value, start_utc, end_utc
            )

        return service_response(True, "Daily entry saved", data = {"entry": entry})


    def _convert_time_to_datetime(self, field: str, value: str) -> datetime:
        if field == "wake_time":
            today = datetime.now(ZoneInfo(self.user_tz)).date()
            return parse_time_to_datetime(value, today, self.user_tz)
        else:
            yesterday = (datetime.now(ZoneInfo(self.user_tz)) - timedelta(days=1)).date()
            return parse_time_to_datetime(value, yesterday, self.user_tz)