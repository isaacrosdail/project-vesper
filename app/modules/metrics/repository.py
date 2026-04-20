from __future__ import annotations

from typing import TYPE_CHECKING, ParamSpec

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session


from sqlalchemy import Integer, cast, func, select

from app.modules.metrics.models import DailyMetrics
from app.shared.repository.base import BaseRepository

P = ParamSpec("P")

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

    def query_one(self, **kwargs) -> DailyMetrics | None:
        results = self.query(**kwargs, limit=1)
        return results[0] if results else None

    def query(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        metric: str | None = None,
        order_by: str = "entry_datetime",
        order: str = "asc",
        limit: int | None = None
    ) -> list[DailyMetrics]:
        stmt = self._user_select(DailyMetrics)

        if start:
            stmt = stmt.where(DailyMetrics.entry_datetime >= start)
        if end:
            stmt = stmt.where(DailyMetrics.entry_datetime < end)
        if metric:
            FILTERABLE_COLS = {"weight", "steps", "calories", "sleep_duration_minutes"}
            # if metric not in self.FILTERABLE_COLS:
            if metric not in FILTERABLE_COLS:
                raise ValueError(f"Unknown metric: {metric}")
            stmt = stmt.where(getattr(DailyMetrics, metric).isnot(None))

        col = getattr(DailyMetrics, order_by)
        stmt = stmt.order_by(col.asc() if order == "asc" else col.desc())

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.execute(stmt).scalars().all())


    def get_latest_daily_metrics_entry(self) -> DailyMetrics | None:
        stmt = self._user_select(DailyMetrics).order_by(DailyMetrics.entry_datetime.desc()).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()


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

        FILTERABLE_COLS = {"weight", "steps", "calories", "sleep_duration_minutes"}
        if metric_type:
            if metric_type not in FILTERABLE_COLS:
                raise ValueError(f"Unknown metric type: {metric_type}")
            column_obj = getattr(DailyMetrics, metric_type)
            stmt = stmt.where(column_obj.isnot(None))
        stmt = stmt.order_by(DailyMetrics.entry_datetime.asc())
        result = self.session.execute(stmt).scalars().all()
        return list(result)

    def get_aggregates_in_window(self, start_utc: datetime, end_utc: datetime) -> dict[str, float] | None:
        """Get average values for each metric field since the given datetime.
        Returns `None` if no entries exist in the window.
        """
        stmt = (
            select(
                func.avg(DailyMetrics.weight).label("weight"),
                func.avg(DailyMetrics.calories).label("calories"),
                func.avg(DailyMetrics.steps).label("steps"),
                func.avg(DailyMetrics.sleep_duration_minutes).label("sleep_duration_minutes")
            )
            .where(
                DailyMetrics.entry_datetime >= start_utc,
                DailyMetrics.entry_datetime < end_utc,
                DailyMetrics.user_id == self.user_id
            )
        )
        result = self.session.execute(stmt).first()
        if result is None or all(v is None for v in result._asdict().values()):
            return None
        return {k: float(v) for k, v in result._asdict().items()}

    # TODO: Study
    def get_bucketed_aggregates(self, start_utc: datetime, end_utc: datetime, num_buckets: int) -> list[dict[str, float]]:
        ## compute boundaries
        # call get_aggregates_in_window once per bucket
        # return list of results
        bucket_size_seconds = (end_utc - start_utc).total_seconds() / num_buckets
        bucket_expr = cast(
            func.extract("epoch", DailyMetrics.entry_datetime - start_utc) / bucket_size_seconds,
            Integer
        )
        stmt = (
            select(
                bucket_expr.label("bucket"),
                func.avg(DailyMetrics.weight).label("weight"),
                func.avg(DailyMetrics.calories).label("calories"),
                func.avg(DailyMetrics.steps).label("steps"),
                func.avg(DailyMetrics.sleep_duration_minutes).label("sleep_duration_minutes")
            )
            .where(
                DailyMetrics.entry_datetime >= start_utc,
                DailyMetrics.entry_datetime < end_utc,
                DailyMetrics.user_id == self.user_id
            )
            .group_by(bucket_expr)
            .order_by(bucket_expr)
        )
        results = self.session.execute(stmt).all()

        ## Now modulate to match shape from before:
        lookup = {
            row.bucket: {
                "weight": float(row.weight) if row.weight else None,
                "calories": float(row.calories) if row.calories else None,
                "steps": float(row.steps) if row.steps else None,
                "sleep_duration_minutes": float(row.sleep_duration_minutes) if row.sleep_duration_minutes else None,
            }
            for row in results
        }

        # dense list
        results = [lookup.get(i) for i in range(num_buckets)]

        # total_duration = end_utc - start_utc # days?
        # bucket_size = total_duration / num_buckets
        # results = []
        # for i in range(num_buckets):
        #     # i=0: start + (0 * 15) -> start + (1 * 15)
        #     # i=1: start + (1 * 15) -> start + (2 * 15)
        #     # i=2: start + (1 * 15) -> start + (2 * 15)
        #     # i=3: start + (1 * 15) -> start + (2 * 15)
        #     bucket_start = start_utc + (bucket_size * i)
        #     bucket_end = start_utc + (bucket_size * (i + 1))
        #     results.append(self.get_aggregates_in_window(bucket_start, bucket_end))
        return results
