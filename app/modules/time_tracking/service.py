
from datetime import timedelta

from app.api.responses import service_response
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.shared.datetime.helpers import now_in_timezone, parse_time_to_datetime


class TimeTrackingService:

    def __init__(self, repository: TimeTrackingRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def save_time_entry(self, typed_data: dict, entry_id: int | None) -> dict:

        # Derived field values
        entry_date = typed_data["entry_date"]
        started_at = parse_time_to_datetime(typed_data["started_at"], entry_date, self.user_tz)
        ended_at = parse_time_to_datetime(typed_data["ended_at"], entry_date, self.user_tz)

        if ended_at < started_at:
            return service_response(
                False,
                "Error: ended_at cannot be earlier than started_at"
            )
        typed_data["started_at"] = started_at
        typed_data["ended_at"] = ended_at

        # Compute duration
        duration = (ended_at - started_at).total_seconds() / 60
        typed_data["duration_minutes"] = int(duration)

        # TODO: Check overlapping time entries
        if False:
            return service_response(
                False,
                "Time entry overlaps with existing entry",
                errors={"started_at": ["Overlaps with existing time entry"]}
            )

        #  UPDATE/PUT
        if entry_id:
            entry = self.repo.get_by_id(entry_id)
            if not entry:
                return service_response(False, "Entry not found")

            for field, value in typed_data.items():
                setattr(entry, field, value)

            return service_response(True, "Time entry updated", data={"entry": entry})

        # CREATE
        else:
            entry = self.repo.create_time_entry(
                category=typed_data["category"],
                description=typed_data.get("description"),
                started_at=typed_data["started_at"],
                ended_at=typed_data["ended_at"],
                duration_minutes=typed_data["duration_minutes"]
            )

        return service_response(True, "Time entry added", data={"entry": entry})