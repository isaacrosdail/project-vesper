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
        wake_datetime: datetime | None = None,
        sleep_datetime: datetime | None = None,
        sleep_duration_minutes: int | None = None,
        calories: int | None = None,
    ) -> DailyMetrics:
        """Create & add new DailyMetrics entry. Returns DailyMetrics entry."""
        entry = DailyMetrics(
            user_id=self.user_id,
            entry_datetime=entry_datetime,
            weight=weight,
            steps=steps,
            wake_datetime=wake_datetime,
            sleep_datetime=sleep_datetime,
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
        self, start_utc: datetime, end_utc: datetime, metric_type: str | None = None
    ) -> list[DailyMetrics]:
        """Returns all DailyMetrics entry in a UTC datetime range. Skips empty rows for given
        metric_type if specified.
        """
        stmt = self._user_select(DailyMetrics).where(
            DailyMetrics.entry_datetime >= start_utc,
            DailyMetrics.entry_datetime < end_utc,
        )
        if metric_type:
            column_obj = getattr(DailyMetrics, metric_type)
            stmt = stmt.where(column_obj.isnot(None))
        stmt = stmt.order_by(DailyMetrics.entry_datetime.asc())
        result = self.session.execute(stmt).scalars().all()
        return list(result)
