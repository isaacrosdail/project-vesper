"""
Repository layer for time_tracking module.
"""
from datetime import datetime, timedelta, timezone

from app.modules.time_tracking.models import TimeEntry
from app.shared.datetime.helpers import last_n_days_range
from app.shared.repository.base import BaseRepository


class TimeTrackingRepository(BaseRepository):
    def __init__(self, session, user_id, user_tz):
        super().__init__(session, user_id, user_tz, model_cls=TimeEntry)
    
    def create_time_entry(self, category: str, started_at: datetime, ended_at: datetime, duration_minutes: float, description: str | None = None):
        time_entry = TimeEntry(
            user_id=self.user_id,
            category=category,
            started_at=started_at,
            duration_minutes=duration_minutes,
            ended_at=ended_at,
            description=description
        )
        return self.add(time_entry)

    def get_all_time_entries_in_window(self, start_utc: datetime, end_utc: datetime):
        stmt = self._user_select(TimeEntry).where(
            TimeEntry.started_at >= start_utc,
            TimeEntry.ended_at < end_utc,
        )
        return self.session.execute(stmt).scalars().all()
 
    def get_entries_by_category_in_window(
            self,
            category: str,
            start_utc: datetime,
            end_utc: datetime,
            order_desc: bool = True,
        ):
        """Get all entries of a given category within a certain datetime window."""
        stmt = self._user_select(TimeEntry).where(
            TimeEntry.category == category,
            TimeEntry.started_at >= start_utc,
            TimeEntry.started_at < end_utc
        )
        if order_desc:
            stmt = stmt.order_by(TimeEntry.started_at.desc())
        return self.session.execute(stmt).scalars().all()