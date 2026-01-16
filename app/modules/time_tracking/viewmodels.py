"""
Presentation layer: Wraps models to provide display-friendly fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from datetime import datetime

    from app.modules.time_tracking.models import TimeEntry


from app.shared.view_mixins import BasePresenter, BaseViewModel


class TimeEntryViewModel(BaseViewModel):
    category: str
    duration_minutes: int
    description: str
    started_at_local: datetime
    ended_at_local: datetime

    def __init__(self, entry: TimeEntry, tz: str) -> None:
        fields = {
            "id",
            "category",
            "duration_minutes",
            "description",
            "started_at_local",
            "ended_at_local",
            "subtype",
        }
        for name in fields:
            setattr(self, name, getattr(entry, name))

        self._tz = tz

    @property
    def date_label(self) -> str:
        return self.started_at_local.strftime("%m/%d")

    @property
    def time_window_label(self) -> str:
        mins = self.duration_minutes
        h, m = divmod(mins, 60)
        duration = f"{h}h{m:02d}m" if h else f"{m}m"
        start = self.started_at_local.strftime("%I:%M%p")
        end = self.ended_at_local.strftime("%I:%M%p")
        return f"{start}-{end} ({duration})"

    @property
    def desc_label(self) -> str:
        return self.description if self.description else "--"


class TimeEntryPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "date",
        "category",
        "time_window",
        "description",
    ]

    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "category": {"label": "Category", "priority": "essential"},
        "description": {"label": "Description", "priority": "essential"},
        "time_window": {
            "label": "Time Window (Duration)",
            "priority": "essential",
            "sort_field": "started_at",
        },
        "date": {"label": "Date", "priority": "essential", "sort_field": "started_at"},
    }
