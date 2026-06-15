from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.time_tracking.models import TimeEntry
    from app.modules.time_tracking.schemas import TimeEntryCreate, TimeEntryPatch


from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

import app.shared.datetime_.helpers as dth
from app.modules.time_tracking.repository import TimeEntryRepository
from app.shared.exceptions import ServiceError
from app.shared.repository.pillar import PillarRepository


class TimeTrackingService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        time_entry_repo: TimeEntryRepository,
        pillar_repo: PillarRepository
    ) -> None:
        self.session = session
        self.time_entry_repo = time_entry_repo
        self.user_tz = user_tz
        self.pillar_repo = pillar_repo


    def create_time_entry(self, validated: TimeEntryCreate) -> TimeEntry:
        started, ended, duration = self._parse_and_validate_times(
            validated.entry_date, validated.started_at, validated.ended_at
        )
        time_entry = self.time_entry_repo.create_time_entry(
            category=validated.category,
            description=validated.description,
            started_at=started,
            ended_at=ended,
            duration_minutes=duration,
        )
        self._sync_pillars(time_entry, validated.pillar_ids)
        return time_entry

    def _parse_and_validate_times(
            self,
            entry_date: date,
            started_at: time,
            ended_at: time,
            exclude_id: int | None = None
        ) -> tuple[datetime, datetime, int]:
        """Parse times, check ordering, check for overlap."""
        start_dt = datetime.combine(entry_date, started_at, tzinfo=ZoneInfo(self.user_tz))
        end_dt = datetime.combine(entry_date, ended_at, tzinfo=ZoneInfo(self.user_tz))

        if end_dt < start_dt:
            end_dt += timedelta(days=1)

        if (end_dt - start_dt).total_seconds() > 24 * 3600:
            raise ServiceError("Time entry cannot exceed 24 hours")

        duration = int((end_dt - start_dt).total_seconds() / 60)

        existing = self.time_entry_repo.get_overlapping_entries(start_dt, end_dt, exclude_id)
        if existing:
            raise ServiceError("Time entry overlap")

        return start_dt, end_dt, duration


    def _sync_pillars(self, time_entry: TimeEntry, pillar_ids: list[int]) -> None:
        time_entry.pillars = self.pillar_repo.get_by_ids(pillar_ids)


    def update_time_entry(self, entry_id: int, validated: TimeEntryPatch) -> TimeEntry:
        entry = self.time_entry_repo.get_by_id(entry_id)
        if not entry:
            raise ServiceError("Time entry not found", 404)

        TIME_FIELDS = {"entry_date", "started_at", "ended_at"}
        if TIME_FIELDS & validated.model_fields_set:
            entry_date = validated.entry_date if "entry_date" in validated.model_fields_set else entry.started_at.astimezone(ZoneInfo(self.user_tz)).date()
            started_at = validated.started_at if "started_at" in validated.model_fields_set else entry.started_at.astimezone(ZoneInfo(self.user_tz)).time()
            ended_at = validated.ended_at if "ended_at" in validated.model_fields_set else entry.ended_at.astimezone(ZoneInfo(self.user_tz)).time()

            started, ended, duration_minutes = self._parse_and_validate_times(entry_date, started_at, ended_at,
                exclude_id=entry_id
            )
            entry.started_at = started
            entry.ended_at = ended
            entry.duration_minutes = duration_minutes

        for field in validated.model_fields_set:
            if field == "pillar_ids":
                self._sync_pillars(entry, validated.pillar_ids)
            elif field in TIME_FIELDS:
                pass  # handled above
            else:
                setattr(entry, field, getattr(validated, field))

        return entry

    def delete_time_entry(self, time_entry_id: int) -> TimeEntry:
        time_entry = self.time_entry_repo.get_by_id(time_entry_id)
        if time_entry is None:
            raise ServiceError("Time entry not found", 404)
        self.time_entry_repo.delete(time_entry)
        return time_entry

    def get_time_entry(self, time_entry_id: int) -> TimeEntry:
        entry = self.time_entry_repo.get_by_id(time_entry_id)
        if entry is None:
            raise ServiceError("Time entry not found", 404)
        return entry

    def get_time_stuff(self) -> pd.DataFrame:
        time_entries = self.time_entry_repo.get_all()

        # build df
        rows = [
            {
                "date": dth.convert_to_timezone(self.user_tz, entry.started_at).date(),
                "duration_minutes": entry.duration_minutes
            }
            for entry in time_entries
        ]
        df = pd.DataFrame(rows)
        # we don't use name= here in reset_index because ["duration_minutes"].sum() produces
        # a Series already named "duration_minutes" (inherits the column name)
        return df.groupby("date")["duration_minutes"].sum().reset_index() # sum duration_mins col per date?


def create_time_tracking_service(
    session: Session, user_id: int, user_tz: str
) -> TimeTrackingService:
    """Factory function to instantiate TimeEntry with required repositories."""
    return TimeTrackingService(
        session=session,
        user_tz=user_tz,
        time_entry_repo=TimeEntryRepository(session, user_id),
        pillar_repo=PillarRepository(session, user_id)
    )
