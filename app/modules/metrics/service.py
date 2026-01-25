from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime
from zoneinfo import ZoneInfo

from app.api.responses import service_response
from app.modules.metrics.repository import DailyMetricsRepository
from app.shared.conversions import lbs_to_kg
from app.shared.datetime import helpers as dth


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
        self, typed_data: dict[str, Any], entry_id: int | None
    ) -> dict[str, Any]:
        """
        Save or update daily metrics entry with sleep/wake time handling.

        Handles datetime conversion for sleep/wake times, automatically adjusting sleep_datetime to previous day when
        it would otherwise occur after wake_datetime (eg, sleep at 22:00, wake at 08:00). Calculates sleep_duration_minutes from
        the adjusted timestamps.
        """
        entry_date: datetime = typed_data.pop("entry_date")

        entry_datetime = datetime(
            entry_date.year, entry_date.month, entry_date.day,
            0, 0, 0,
            tzinfo=ZoneInfo(self.user_tz)
        )
        typed_data["entry_datetime"] = entry_datetime

        for key in ("wake_datetime", "sleep_datetime"):
            if typed_data.get(key):
                typed_data[key] = typed_data[key].replace(tzinfo=ZoneInfo(self.user_tz))

        wake = typed_data.get("wake_datetime")
        sleep = typed_data.get("sleep_datetime")

        if sleep and wake:
            sleep_duration = typed_data["wake_datetime"] - typed_data["sleep_datetime"]
            typed_data["sleep_duration_minutes"] = int(
                sleep_duration.total_seconds() / 60
            )

        # Always store weight in kg
        if "weight" in typed_data:
            if "weight_units" not in typed_data:
                return service_response(
                    success=False,
                    message="Error converting weight: Missing weight_units",
                )
            typed_data["weight"] = self._convert_weight(
                typed_data["weight"], typed_data.pop("weight_units")
            )

        # Get UTC window for duplicate checking plus grab entry to compare against, if any
        start_utc, end_utc = dth.day_range_utc(
            typed_data["entry_datetime"], self.user_tz
        )
        existing_metrics_entry = self.daily_metrics_repo.get_daily_metrics_in_window(
            start_utc, end_utc
        )

        # UPDATE
        if entry_id is not None:
            entry = self.daily_metrics_repo.get_by_id(entry_id)
            if not entry:
                return service_response(
                    success=False, message="Daily metrics entry not found"
                )

            if existing_metrics_entry and existing_metrics_entry.id != entry_id:
                return service_response(
                    success=False,
                    message="Error: An entry already exists for this date",
                )

            self._update_fields(entry, typed_data)

            return service_response(
                success=True,
                message="Daily metrics entry updated",
                data={"entry": entry},
            )

        # CREATE
        if existing_metrics_entry:
            self._update_fields(existing_metrics_entry, typed_data)
            entry = existing_metrics_entry
        else:
            entry = self.daily_metrics_repo.create_daily_metrics(**typed_data)

        return service_response(
            success=True, message="Daily metrics entry saved", data={"entry": entry}
        )

    def _update_fields(self, entry: Any, typed_data: dict[str, Any]) -> Any:
        for field, value in typed_data.items():
            setattr(entry, field, value)
        return entry

    def _convert_weight(self, weight: float, units: str) -> float:
        """Always store master units in kg."""
        if units == "lbs":
            return lbs_to_kg(weight)
        return weight


def create_metrics_service(
    session: Session, user_id: int, user_tz: str
) -> MetricsService:
    """Factory function to instantiate MetricsService with required repositories."""
    return MetricsService(
        session=session,
        user_tz=user_tz,
        daily_metrics_repo=DailyMetricsRepository(session, user_id),
    )
