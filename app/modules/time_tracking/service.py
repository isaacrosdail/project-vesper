
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.api.responses import service_response
from app.modules.time_tracking.repository import TimeEntryRepository
from app.shared.datetime.helpers import parse_time_to_datetime, day_range_utc


class TimeTrackingService:
    def __init__(
        self,
        session: 'Session',
        user_tz: str,
        time_entry_repo: TimeEntryRepository, 
    ):
        self.session = session
        self.time_entry_repo = time_entry_repo
        self.user_tz = user_tz

    def save_time_entry(self, typed_data: dict[str, Any], entry_id: int | None) -> dict[str, Any]:

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

        duration = (ended_at - started_at).total_seconds() / 60
        typed_data["duration_minutes"] = int(duration)

        # Reject overlapping time entries
        start_utc, end_utc = day_range_utc(entry_date, self.user_tz)
        existing_entries = self.time_entry_repo.get_all_time_entries_in_window(start_utc, end_utc)
        for entry in existing_entries:
            if entry_id and entry.id == entry_id: # skip checking against self
                continue
            # Allow entries that touch at endpoints (eg, 11:00-12:00 then 12:00-13:00)
            if (typed_data["started_at"] < entry.ended_at and typed_data["ended_at"] > entry.started_at):
                return service_response(False, "Time entry overlap detected")

        #  UPDATE/PUT
        if entry_id:
            existing_entry = self.time_entry_repo.get_by_id(entry_id)
            if not existing_entry:
                return service_response(False, "Existing entry to be updated was not found")

            for field, value in typed_data.items():
                setattr(existing_entry, field, value)

            return service_response(True, "Time entry updated", data={"entry": existing_entry})

        # CREATE
        else:
            entry = self.time_entry_repo.create_time_entry(
                category=typed_data["category"],
                description=typed_data.get("description"),
                started_at=typed_data["started_at"],
                ended_at=typed_data["ended_at"],
                duration_minutes=typed_data["duration_minutes"]
            )

        return service_response(True, "Time entry added", data={"entry": entry})


def create_time_tracking_service(session: 'Session', user_id: int, user_tz: str) -> TimeTrackingService:
    """Factory function to instantiate TimeEntry with required repositories."""
    return TimeTrackingService(
        session=session,
        user_tz=user_tz,
        time_entry_repo=TimeEntryRepository(session, user_id),
    )