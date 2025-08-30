
from datetime import datetime, time

from app.shared.repository.base import BaseRepository

from .models import DailyEntry


class DailyMetricsRepository(BaseRepository):

    def get_all_daily_metrics(self):
        """Return all DailyEntry entries."""
        return self.session.query(DailyEntry).filter(
            DailyEntry.user_id == self.user_id
        ).all()

    def get_metrics_by_type_in_window(self, metric_type: str, start_utc: datetime, end_utc: datetime):
        if not hasattr(DailyEntry, metric_type):
            raise ValueError(f"DailyEntry has no column '{metric_type}'")

        column_obj = getattr(DailyEntry, metric_type) # gives us our desired SQLAlchemy column object
        return self.session.query(DailyEntry).filter(
            DailyEntry.user_id == self.user_id,
            column_obj.isnot(None),
            DailyEntry.created_at >= start_utc,
            DailyEntry.created_at < end_utc
        ).all()
    
    def create_or_update_daily_metric(self, metric_type: str, value: int | float | time, start_utc: datetime, end_utc: datetime):
        """Create new daily metric or update existing one for given date."""
        existing = self.get_metric_by_type_for_day(metric_type, start_utc, end_utc)
        if existing:
            setattr(existing, metric_type, value) # dynamically set existing.weight = value
            return existing
        else:
            return self.create_daily_metric(metric_type, value)
        
    def create_daily_metric(self, metric_type: str, value: int | float | time):
        """Create & add a new daily metric. Returns metric."""
        metric = DailyEntry(
            user_id=self.user_id,
            **{metric_type: value} # **kwargs unpacks this to the actual values at runtime
            # So if metric_type="weight" and value=170, it unpacks to => weight=170
        )
        self.session.add(metric)
        return metric 

    def get_metric_by_type_for_day(self, metric_type: str, start_utc: datetime, end_utc: datetime):
        """Get single daily metric of given type for specific day."""
        if not hasattr(DailyEntry, metric_type):
            raise ValueError(f"DailyEntry has no column '{metric_type}'")
        column_obj = getattr(DailyEntry, metric_type)
        return self.session.query(DailyEntry).filter(
            DailyEntry.user_id == self.user_id,
            column_obj.isnot(None),
            DailyEntry.created_at >= start_utc,
            DailyEntry.created_at < end_utc
        ).first()