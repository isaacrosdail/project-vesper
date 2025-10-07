
from datetime import timedelta

from app.api.responses import service_response
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.shared.datetime.helpers import now_in_timezone, parse_time_to_datetime


class TimeTrackingService:

    def __init__(self, repository: TimeTrackingRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def create_entry_from_form(self, typed_data: dict) -> dict:

        # Transform raw input -> domain values
        today = now_in_timezone(self.user_tz)
        started_at = parse_time_to_datetime(typed_data["started_at"], today, self.user_tz)
        ended_at = started_at + timedelta(minutes=typed_data["duration_minutes"])

        # TODO: Check overlapping time entries
        if False:
            return service_response(
                False,
                "Time entry overlaps with existing entry",
                errors={"started_at": ["Overlaps with existing time entry"]}
            )

        # Persist
        entry = self.repo.create_time_entry(
            category=typed_data["category"],
            description=typed_data.get("description"),
            started_at=started_at,
            ended_at=ended_at,
            duration_minutes=typed_data["duration_minutes"]
        )
        return service_response(True, "Time entry added", data={"entry": entry})