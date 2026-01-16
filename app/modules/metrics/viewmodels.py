from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from datetime import datetime

    from app.modules.metrics.models import DailyMetrics


from app.shared.view_mixins import BasePresenter, BaseViewModel


class DailyMetricPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "entry_datetime",
        "weight",
        "steps",
        "wake_time",
        "sleep_time",
        "calories",
    ]

    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "entry_datetime": {"label": "Date", "priority": "essential"},
        "updated_at": {"label": "Last Updated", "priority": "desktop-only"},
        "weight": {"label": "Weight", "priority": "essential"},
        "steps": {"label": "Steps", "priority": "essential"},
        "wake_time": {"label": "Wake Time", "priority": "essential"},
        "sleep_time": {"label": "Sleep Time", "priority": "essential"},
        "calories": {"label": "Calories", "priority": "essential"},
    }


class DailyMetricViewModel(BaseViewModel):
    entry_datetime: datetime
    weight: int
    steps: int
    wake_time_local: datetime
    sleep_time_local: datetime
    calories: int | None
    subtype: str

    def __init__(self, metric: DailyMetrics, tz: str) -> None:
        fields = {
            "id",
            "weight",
            "steps",
            "wake_time_local",
            "sleep_time_local",
            "calories",
            "subtype",
        }
        for name in fields:
            setattr(self, name, getattr(metric, name))

        self.created_at_local = metric.entry_datetime_local
        self._tz = tz

    @property
    def entry_datetime_label(self) -> str:
        return self.format_created_at_label()

    @property
    def weight_label(self) -> str:
        return f"{self.weight:.2f}" if self.weight else "--"

    @property
    def steps_label(self) -> str:
        return str(self.steps) if self.steps is not None else "--"

    @property
    def wake_time_label(self) -> str:
        return (
            self.wake_time_local.strftime("%H:%M")
            if self.wake_time_local is not None
            else "--"
        )

    @property
    def sleep_time_label(self) -> str:
        return (
            self.sleep_time_local.strftime("%H:%M")
            if self.sleep_time_local is not None
            else "--"
        )

    @property
    def calories_label(self) -> str:
        if self.calories is None:
            return "--"

        calories_int = round(self.calories)
        return str(calories_int)
