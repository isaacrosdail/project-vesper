from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session

from sqlalchemy import select

from app.modules.metrics.models import DailyMetrics
from app.shared.repository.base import BaseRepository


class DailyMetricsRepository(BaseRepository[DailyMetrics]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=DailyMetrics)

    def create_daily_metrics(
        self,
        entry_datetime: datetime,
        weight: float | None = None,
        steps: int | None = None,
        wake_time: datetime | None = None,
        sleep_time: datetime | None = None,
        sleep_duration_minutes: int | None = None,
        calories: int | None = None,
    ) -> DailyMetrics:
        """Create & add new DailyMetrics entry. Returns DailyMetrics entry."""
        entry = DailyMetrics(
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

    def get_daily_metrics_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> DailyMetrics | None:
        """Returns the first DailyMetrics entry in a UTC datetime range."""
        stmt = self._user_select(DailyMetrics).where(
            DailyMetrics.entry_datetime >= start_utc,
            DailyMetrics.entry_datetime < end_utc,
        )
        return self.session.execute(stmt).scalars().first()

    def get_all_daily_metrics_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> list[DailyMetrics]:
        """Returns the first DailyMetrics entry in a UTC datetime range."""
        stmt = self._user_select(DailyMetrics).where(
            DailyMetrics.entry_datetime >= start_utc,
            DailyMetrics.entry_datetime < end_utc,
        )
        result = self.session.execute(stmt).scalars().all()
        return list(result)

    def get_daily_metrics_by_type_in_window(
        self, metric_type: str, start_utc: datetime, end_utc: datetime
    ) -> list[Any]:
        """Returns list of (entry_datetime, <metric_value>) tuples for a given metric type."""
        column_obj = getattr(DailyMetrics, metric_type)

        stmt = (
            select(DailyMetrics.entry_datetime, column_obj)
            .where(
                DailyMetrics.user_id == self.user_id,
                DailyMetrics.entry_datetime >= start_utc,
                DailyMetrics.entry_datetime < end_utc,
                column_obj.isnot(None),
            )
            .order_by(DailyMetrics.entry_datetime)
        )

        return list(self.session.execute(stmt).all())
