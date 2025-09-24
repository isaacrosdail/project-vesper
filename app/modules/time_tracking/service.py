from datetime import datetime

from app.modules.time_tracking.models import TimeEntry
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.validators import validate_time_entry
from app.shared.datetime.helpers import parse_datetime_from_hhmm, add_mins_to_datetime

class TimeTrackingService:

    def __init__(self, repository: TimeTrackingRepository):
        self.repo = repository

    def create_entry_from_form(self, form_data: dict, user_timezone: str) -> dict:

        errors = validate_time_entry(form_data)
        if errors:
            return {"success": False, "message": errors[0]}
        
        try:
            # Transform raw input -> domain values
            started_at = parse_datetime_from_hhmm(form_data["started_at"], user_timezone)
            duration_minutes = float(form_data["duration"])
            ended_at = add_mins_to_datetime(started_at, duration_minutes)
        except (ValueError, KeyError):
            return {"success": False, "message": "Invalid time or duration format"}
        
        # Business validation (eg, handling overlapping times, etc)

        # Persist via repo
        entry = self.repo.create_time_entry(
            category=form_data.get("category").strip(),
            description=form_data.get("description").strip(),
            started_at=started_at,
            ended_at=ended_at,
            duration=duration_minutes
        )

        # Return success + created entry
        return {
            "success": True,
            "entry": entry
        }