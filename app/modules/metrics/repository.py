
from datetime import datetime, timedelta
from decimal import Decimal

from app.shared.repository.base import BaseRepository

from app.modules.metrics.models import DailyEntry


class DailyMetricsRepository(BaseRepository):
    def __init__(self, session, user_id, user_tz):
        super().__init__(session, user_id, user_tz, model_cls=DailyEntry)

    def get_all_daily_metrics(self):
        return self.get_all()
    
    def get_daily_metric_by_id(self, entry_id: int):
        return self.get_by_id(entry_id)
    
    def get_daily_metric_in_window(self, start_utc: datetime, end_utc: datetime):
        return self._user_query(DailyEntry).filter(
            DailyEntry.entry_datetime >= start_utc,
            DailyEntry.entry_datetime < end_utc
        ).first()


    def get_metrics_by_type_in_window(self, metric_type: str, start_utc: datetime, end_utc: datetime):
        """Returns list of tuples (entry_datetime, metric_type_value)"""
        column_obj = getattr(DailyEntry, metric_type)
        
        return self._user_query(DailyEntry)\
            .with_entities(DailyEntry.entry_datetime, column_obj)\
            .filter(
                column_obj.isnot(None),
                DailyEntry.entry_datetime >= start_utc,
                DailyEntry.entry_datetime < end_utc
            )\
            .order_by(DailyEntry.entry_datetime)\
            .all()


    def create_daily_metric(
            self,
            entry_datetime: datetime,
            weight: Decimal | None = None,
            steps: int | None = None,
            wake_time: datetime | None = None,
            sleep_time: datetime | None = None,
            sleep_duration_minutes: int | None = None,
            calories: int | None = None,
    ) -> DailyEntry:
        """Create & add a new daily metric. Returns metric."""
        entry = DailyEntry(
            user_id=self.user_id,
            entry_datetime=entry_datetime,
            weight=weight,
            steps=steps,
            wake_time=wake_time,
            sleep_time=sleep_time,
            sleep_duration_minutes=sleep_duration_minutes,
            calories=calories,
        )
        return self.add(entry)