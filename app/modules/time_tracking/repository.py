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


    def get_all_time_entries(self):
        return self.get_all()


    def get_all_time_entries_in_window(self, start_utc: datetime, end_utc: datetime):
        return self._user_query(TimeEntry).filter(
            TimeEntry.started_at >= start_utc,
            TimeEntry.ended_at < end_utc,
        ).all()

    
    def get_entries_by_category_in_window(self, category: str, start_utc: datetime, end_utc: datetime):
        """Get all entries of a given category within a certain datetime window."""
        return self._user_query(TimeEntry).filter(
            TimeEntry.category == category,
            TimeEntry.started_at >= start_utc,
            TimeEntry.started_at < end_utc
        ).all()

    
    def get_entries_by_category_last_n_days(self, category: str, days_ago: int):
        """
        Get time entries of given category within last N calendar days, ordered by date.
        Inclusive of today so far.
        Uses started_at
        """
        start_utc, end_utc = last_n_days_range(days_ago, self.user_tz)
        return self._user_query(TimeEntry).filter(
            TimeEntry.started_at >= start_utc,
            TimeEntry.started_at < end_utc,
        ).order_by(
            TimeEntry.started_at.desc()
        ).all()