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
        # typed_data["entry_date"] is already a datetime.date obj from validators
        entry_date = typed_data.pop("entry_date")

        entry_datetime = datetime(
            entry_date.year, entry_date.month, entry_date.day,
            0, 0, 0,
            tzinfo=ZoneInfo(self.user_tz)
        )
        typed_data["entry_datetime"] = entry_datetime

        # Convert wake/sleep times to full datetimes
        # NOTE: Currently assuming wake_time belongs to entry date, and sleep_time to the night prior
        if "wake_time" in typed_data:
            day_of = typed_data["entry_datetime"].date()
            typed_data["wake_time"] = parse_time_to_datetime(typed_data["wake_time"], day_of, self.user_tz)
        if "sleep_time" in typed_data:
            prev_day = (typed_data["entry_datetime"] - timedelta(days=1)).date()
            typed_data["sleep_time"] = parse_time_to_datetime(typed_data["sleep_time"], prev_day, self.user_tz)

        # Check wake/sleep times are sensible
        if "wake_time" in typed_data and "sleep_time" in typed_data:

            if typed_data["wake_time"] <= typed_data["sleep_time"]:
                return service_response(
                    False,
                    "Wake/Sleep time check failed",
                    errors={
                        "wake_time": [WAKE_MUST_BE_AFTER_SLEEP],
                        "sleep_time": [WAKE_MUST_BE_AFTER_SLEEP]
                    }
                )
            
            ## Calc sleep_duration_minutes
            duration = typed_data["wake_time"] - typed_data["sleep_time"]
            typed_data["sleep_duration_minutes"] = int(duration.total_seconds() / 60)

        ## Check for existing entry
        # UPDATE
        if entry_id is not None:
            entry = self.repo.get_by_id(entry_id)
            if not entry:
                return service_response(False, "Daily entry not found")
            
            # Also fail if an entry for that date already exists.
            entry_datetime_utc = typed_data["entry_datetime"].astimezone(ZoneInfo("UTC"))
            start_utc, end_utc = entry_datetime_utc, (entry_datetime_utc + timedelta(days=1))

            existing_entry = self.repo.get_daily_metric_in_window(start_utc, end_utc)
            if existing_entry and existing_entry.id != entry_id:
                return service_response(
                    False,
                    "Error: An entry already exists for this date",
                )
            
            for field, value in typed_data.items():
                setattr(entry, field, value)
    
            return service_response(True, "Daily entry updated", data={"entry": entry})
    
        # CREATE/UPSERT (for today)
        # If an entry for that date exists already, update/overwrite it
        entry_datetime_utc = typed_data["entry_datetime"].astimezone(ZoneInfo("UTC"))
        start_utc, end_utc = entry_datetime_utc, (entry_datetime_utc + timedelta(days=1))

        existing_entry = self.repo.get_daily_metric_in_window(start_utc, end_utc)
        if existing_entry:
            for field, value in typed_data.items():
                setattr(existing_entry, field, value)
            entry = existing_entry
        else:
            entry = self.repo.create_daily_metric(**typed_data)

        return service_response(True, "Daily entry saved", data = {"entry": entry})