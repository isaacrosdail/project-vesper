
from datetime import timedelta

from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.validators import validate_time_entry
from app.shared.datetime.helpers import parse_time_to_datetime, now_in_timezone
from app.modules.api.responses import service_response


class TimeTrackingService:

    def __init__(self, repository: TimeTrackingRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def create_entry_from_form(self, data: dict) -> dict:

        errors = validate_time_entry(data)
        if errors:
            return service_response(False, "Validation failed", errors=errors)
        
        try:
            # Transform raw input -> domain values
            today = now_in_timezone(self.user_tz)
            started_at = parse_time_to_datetime(data["started_at"], today, self.user_tz)
            duration_minutes = float(data["duration_minutes"])
            ended_at = started_at + timedelta(minutes=duration_minutes)
        except (ValueError, KeyError):
            return service_response(False, "Time/duration error", data={"general": ["Invalid time or duration format"]})
        
        # Business validation (eg, handling overlapping times, etc)

        # Persist via repo
        entry = self.repo.create_time_entry(
            category=data["category"],
            description=data["description"],
            started_at=started_at,
            ended_at=ended_at,
            duration_minutes=duration_minutes
        )
        return service_response(True, "Time entry added", data={"entry": entry})