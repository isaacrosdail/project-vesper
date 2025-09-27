
from datetime import datetime, time

from app.shared.repository.base import BaseRepository

from .models import DailyEntry


class DailyMetricsRepository(BaseRepository):
    def __init__(self, session, user_id, user_tz):
        super().__init__(session, user_id, user_tz, model_cls=DailyEntry)

    def get_all_daily_metrics(self):
        return self.get_all()

    # def get_all_daily_metrics(self):
    #     """Return all DailyEntry entries."""
    #     return self.session.query(DailyEntry).filter(
    #         DailyEntry.user_id == self.user_id
    #     ).all()

    # TODO
    def get_metrics_by_type_in_window(self, metric_type: str, start_utc: datetime, end_utc: datetime):
        # TODO: Move to validators/service layer, similar to below
        if not hasattr(DailyEntry, metric_type):
            raise ValueError(f"DailyEntry has no column '{metric_type}'")

        column_obj = getattr(DailyEntry, metric_type) # gives us our desired SQLAlchemy column object
        
        return self._user_query(DailyEntry).filter(
            column_obj.isnot(None),
            DailyEntry.created_at >= start_utc,
            DailyEntry.created_at < end_utc
        ).all()

    # TODO
    def create_or_update_daily_metric(self, metric_type: str, value: int | float | time, start_utc: datetime, end_utc: datetime):
        """Create new daily metric or update existing one for given date. Returns tuple (entry, was_created)."""
        # TODO: Move this check to validators/service layer
        if not hasattr(DailyEntry, metric_type):
            raise ValueError(f"Invalid metric: {metric_type}")
        
        entry = self.get_daily_entry_for_day(start_utc, end_utc)

        if entry:
            setattr(entry, metric_type, value) # dynamically set entry.weight = value
            return entry, False
        else:
            entry = DailyEntry(user_id=self.user_id, **{metric_type: value})
            return self.add(entry), True

        
    def create_daily_metric(self, metric_type: str, value: int | float | time):
        """Create & add a new daily metric. Returns metric."""
        metric = DailyEntry(
            user_id=self.user_id,
            **{metric_type: value}
        )
        return self.add(metric)


    def get_daily_entry_for_day(self, start_utc: datetime, end_utc: datetime):
        """Get DailyMetric for a given window."""
        return self.session.query(DailyEntry).filter(
            DailyEntry.user_id == self.user_id,
            DailyEntry.created_at >= start_utc,
            DailyEntry.created_at < end_utc
        ).first()