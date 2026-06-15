from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.metrics.models import DailyMetrics

from datetime import datetime
from zoneinfo import ZoneInfo

from app.modules.metrics.models import MetricType, WeightUnitsEnum
from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.schemas import DailyMetricsCreate
from app.shared.datetime_ import helpers as dth
from app.shared.exceptions import ServiceError
from app.shared.utils import lbs_to_kg


class MetricsService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        daily_metrics_repo: DailyMetricsRepository,
    ) -> None:
        self.session = session
        self.user_tz = user_tz
        self.daily_metrics_repo = daily_metrics_repo

    def save_daily_metrics(
        self, validated: DailyMetricsCreate, entry_id: int | None
    ) -> tuple[DailyMetrics, bool]:
        """
        Save or update daily metrics entry with sleep/wake time handling.

        Handles datetime conversion for sleep/wake times, automatically adjusting sleep_datetime to previous day when
        it would otherwise occur after wake_datetime (eg, sleep at 22:00, wake at 08:00). Calculates sleep_duration_minutes from
        the adjusted timestamps.
        """
        user_tz_obj = ZoneInfo(self.user_tz)
        # entry_date: datetime = typed_data.pop("entry_date")
        entry_datetime = datetime(
            validated.entry_date.year, validated.entry_date.month, validated.entry_date.day,
            0, 0, 0,
            tzinfo=user_tz_obj
        )
        # typed_data["entry_datetime"] = entry_datetime

        # Making sleep/wake tz-aware, if they exist in validated
        wake = validated.wake_datetime.replace(tzinfo=user_tz_obj) if validated.wake_datetime else None
        sleep = validated.sleep_datetime.replace(tzinfo=user_tz_obj) if validated.sleep_datetime else None
        sleep_duration_minutes = int((wake - sleep).total_seconds() / 60) if sleep and wake else None
        # If both sleep and wake, find sleep duration
        # # sleep_duration_minutes = None
        # if sleep and wake:
        #     sleep_duration_minutes = int((wake - sleep).total_seconds() / 60)

        # Always store weight in kg
        weight = validated.weight
        if "weight" in validated.model_fields_set and weight is not None and validated.weight_units is WeightUnitsEnum.LBS:
            weight = lbs_to_kg(weight)

        # Find or create entry
        start_utc, end_utc = dth.day_range_utc(entry_datetime, self.user_tz)
        entry = (self.daily_metrics_repo.get_by_id(entry_id) if entry_id
                else self.daily_metrics_repo.query_one(start=start_utc, end=end_utc))

        is_new = entry is None
        if is_new:
            entry = self.daily_metrics_repo.create_daily_metrics(
                entry_datetime=entry_datetime,
                weight=weight,
                steps=validated.steps,
                wake_datetime=validated.wake_datetime,
                sleep_datetime=validated.sleep_datetime,
                sleep_duration_minutes=sleep_duration_minutes,
                calories=validated.calories,
            )
            self.session.flush()
            return entry, is_new

        if not entry:
            raise ServiceError("Error: no entry found")
        # Update only sent fields
        entry.entry_datetime = entry_datetime
        entry.wake_datetime = wake
        entry.sleep_datetime = sleep
        entry.sleep_duration_minutes = sleep_duration_minutes

        for field in validated.model_fields_set:
            if field in {"entry_date", "weight_units", "wake_datetime", "sleep_datetime"}:
                continue  # handled above
            if field == "weight":
                entry.weight = weight  # use converted value
                continue
            setattr(entry, field, getattr(validated, field))

        return entry, is_new



    def get_daily_metrics(self, *, start: datetime | None = None, end: datetime | None = None, metric: MetricType | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        entries = self.daily_metrics_repo.query(start=start, end=end, metric=metric, limit=limit)
        if metric:
            return [
                {
                    "date": e.entry_datetime.isoformat(timespec="seconds"),
                    "value": getattr(e, metric)
                }
                for e in entries
            ]
        return [e.to_api_dict() for e in entries]

    def get_daily_metrics_entry(self, entry_id: int) -> DailyMetrics:
        entry = self.daily_metrics_repo.get_by_id(entry_id)
        if entry is None:
            raise ServiceError("Daily metrics not found", 404)
        return entry
    
    def delete_daily_metrics(self, daily_metrics_id: int) -> DailyMetrics:
        daily_metrics = self.daily_metrics_repo.get_by_id(daily_metrics_id)
        if daily_metrics is None:
            raise ServiceError("Daily metrics entry not found", 404)
        self.daily_metrics_repo.delete(daily_metrics)
        return daily_metrics


def create_metrics_service(
    session: Session, user_id: int, user_tz: str
) -> MetricsService:
    """Factory function to instantiate MetricsService with required repositories."""
    return MetricsService(
        session=session,
        user_tz=user_tz,
        daily_metrics_repo=DailyMetricsRepository(session, user_id),
    )
