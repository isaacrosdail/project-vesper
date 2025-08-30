"""
Repository layer for time_tracking module.
"""
from datetime import datetime, timedelta, timezone

from app.modules.time_tracking.models import TimeEntry
from app.shared.datetime.helpers import last_n_days_range, start_of_day_utc
from app.shared.repository.base import BaseRepository


class TimeTrackingRepository(BaseRepository):
    
    def create_time_entry(self, category: str, started_at: datetime, ended_at: datetime, duration: float, description: str | None = None):
        new_time_entry = TimeEntry(
            user_id=self.user_id,
            category=category,
            started_at=started_at,
            duration=duration,
            ended_at=ended_at,
            description=description
        )
        self.session.add(new_time_entry)
        return new_time_entry

    def get_all_time_entries(self):
        return self.session.query(TimeEntry).filter(
            TimeEntry.user_id == self.user_id
        ).all()
    
    def get_all_time_entries_in_window(self, start_utc: datetime, end_utc: datetime):
        return self.session.query(TimeEntry).filter(
            TimeEntry.user_id == self.user_id,
            TimeEntry.started_at >= start_utc,
            TimeEntry.ended_at < end_utc,
        ).all()
    
    def get_entries_by_category_in_window(self, category: str, start_utc: datetime, end_utc: datetime):
        """Get all entries of a given category within a certain datetime window."""
        return self.session.query(TimeEntry).filter(
            TimeEntry.user_id == self.user_id,
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
        return self.session.query(TimeEntry).filter(
            TimeEntry.user_id == self.user_id,
            TimeEntry.started_at >= start_utc,
            TimeEntry.started_at < end_utc,
            ).order_by(TimeEntry.started_at.desc()).all()