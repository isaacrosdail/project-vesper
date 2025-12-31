
from typing import Any

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.modules.metrics.repository import DailyMetricsRepository
from app.shared.datetime.helpers import parse_time_to_datetime
from app.api.responses import service_response


class DailyMetricsService:
    def __init__(self, repository: DailyMetricsRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def save_daily_entry(self, typed_data: dict[str, Any], entry_id: int | None) -> dict[str, Any]:
        """
        Save or update daily metrics entry with sleep/wake time handling.

        Handles datetime conversion for sleep/wake times, automatically adjusting sleep_time to previous day when
        it would otherwise occur after wake_time (eg, sleep at 22:00, wake at 08:00). Calculates sleep_duration_minutes from
        the adjusted timestamps.
        """
        entry_date: datetime = typed_data.pop("entry_date")

        entry_datetime = datetime(
            entry_date.year, entry_date.month, entry_date.day,
            0, 0, 0,
            tzinfo=ZoneInfo(self.user_tz)
        )
        typed_data["entry_datetime"] = entry_datetime

        day_of = typed_data["entry_datetime"].date()
        if "wake_time" in typed_data:
            typed_data["wake_time"] = parse_time_to_datetime(typed_data["wake_time"], day_of, self.user_tz)
        if "sleep_time" in typed_data:
            typed_data["sleep_time"] = parse_time_to_datetime(typed_data["sleep_time"], day_of, self.user_tz)

        # Assign sleep_time dt to yesterday for cases where sleep_time >= wake_time
        if "wake_time" in typed_data and "sleep_time" in typed_data:
            if typed_data["sleep_time"] >= typed_data["wake_time"]:
                typed_data["sleep_time"] -= timedelta(days=1)

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