"""
Repository layer for time_tracking module.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime

from app.modules.time_tracking.models import TimeEntry
from app.shared.repository.base import BaseRepository


class TimeEntryRepository(BaseRepository[TimeEntry]):
    def __init__(self, session: 'Session', user_id: int):
        super().__init__(session, user_id, model_cls=TimeEntry)
    
    def create_time_entry(self, category: str, started_at: datetime, ended_at: datetime, duration_minutes: float, description: str | None = None) -> TimeEntry:
        time_entry = TimeEntry(
            user_id=self.user_id,
            category=category,
            started_at=started_at,
            duration_minutes=duration_minutes,
            ended_at=ended_at,
            description=description
        )
        return self.add(time_entry)

    def get_all_time_entries_in_window(self, start_utc: datetime, end_utc: datetime) -> list[TimeEntry]:
        stmt = self._user_select(TimeEntry).where(
            TimeEntry.started_at >= start_utc,
            TimeEntry.ended_at < end_utc,
        )
        return list(self.session.execute(stmt).scalars().all())
 
    def get_entries_by_category_in_window(
            self,
            category: str,
            start_utc: datetime,
            end_utc: datetime,
            order_desc: bool = True,
        ) -> list[TimeEntry]:
        """Get all entries of a given category within a certain datetime window."""
        stmt = self._user_select(TimeEntry).where(
            TimeEntry.category == category,
            TimeEntry.started_at >= start_utc,
            TimeEntry.started_at < end_utc
        )
        if order_desc:
            stmt = stmt.order_by(TimeEntry.started_at.desc())
        return list(self.session.execute(stmt).scalars().all())