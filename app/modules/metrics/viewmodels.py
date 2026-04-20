from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from app.modules.metrics.models import DailyMetrics

from app.modules.auth.models import UnitSystemEnum
from app.shared.utils import kg_to_lbs
from app.shared.view_mixins import BasePresenter, BaseViewModel


class DailyMetricPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "entry_datetime",
        "weight",
        "steps",
        "wake_datetime",
        "sleep_datetime",
        "calories",
    ]

    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "entry_datetime": {"label": "Date", "priority": "essential"},
        "updated_at": {"label": "Last Updated", "priority": "desktop-only"},
        "weight": {"label": "Weight", "priority": "essential"},
        "steps": {"label": "Steps", "priority": "essential"},
        "wake_datetime": {"label": "Wake Time", "priority": "essential"},
        "sleep_datetime": {"label": "Sleep Time", "priority": "essential"},
        "calories": {"label": "Calories", "priority": "essential"},
    }


class DailyMetricViewModel(BaseViewModel):
    __slots__ = (
        "calories",
        "entry_datetime_local",
        "id",
        "sleep_datetime_local",
        "sleep_duration_minutes",
        "steps",
        "subtype",
        "units",
        "wake_datetime_local",
        "weight",
    )

    def __init__(self, metric: DailyMetrics, tz: str, units: UnitSystemEnum) -> None:
        self.weight = metric.weight
        self.steps = metric.steps
        self.wake_datetime_local = metric.wake_datetime_local
        self.sleep_datetime_local = metric.sleep_datetime_local
        self.sleep_duration_minutes = metric.sleep_duration_minutes
        self.calories = metric.calories
        self.subtype = metric.subtype
        self.created_at_local = metric.entry_datetime_local
        self.id = metric.id
        self._tz = tz
        self.units = units

    @property
    def entry_datetime_label(self) -> str:
        return self.format_created_at_label()

    @property
    def weight_label(self) -> str:
        if not self.weight:
            return "--"
        display = kg_to_lbs(self.weight) if self.units is UnitSystemEnum.IMPERIAL else self.weight
        suffix = "lbs" if self.units is UnitSystemEnum.IMPERIAL else "kg"
        return f"{display:.1f} {suffix}"


    @property
    def steps_label(self) -> str:
        return str(self.steps) if self.steps is not None else "--"

    @property
    def wake_datetime_label(self) -> str:
        return (
            self.wake_datetime_local.strftime("%H:%M")
            if self.wake_datetime_local is not None
            else "--"
        )

    @property
    def sleep_datetime_label(self) -> str:
        return (
            self.sleep_datetime_local.strftime("%H:%M")
            if self.sleep_datetime_local is not None
            else "--"
        )

    @property
    def calories_label(self) -> str:
        if self.calories is None:
            return "--"

        calories_int = round(self.calories)
        return str(calories_int)
