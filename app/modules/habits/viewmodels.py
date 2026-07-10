from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:

    from app.modules.habits.models import Habit


from app.shared.view_mixins import BasePresenter, BaseViewModel


class HabitPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = ["name", "status", "created_at"]

    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "name": {"label": "Name", "priority": "essential"},
        "tags": {"label": "Tag(s)", "priority": "desktop-only"},
        "status": {"label": "Status", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "established_date": {"label": "Date Promoted", "priority": "desktop-only"},
        "promotion_threshold": {
            "label": "Promotion Threshold",
            "priority": "desktop-only",
        },
    }


class HabitViewModel(BaseViewModel):
    __slots__ = (
        "established_date",
        "id",
        "name",
        # "promotion_threshold",
        "status",
        "subtype"
    )

    def __init__(self, habit: Habit, tz: str) -> None:
        self.id = habit.id
        self.name = habit.name
        self.status = habit.status
        self.established_date = habit.established_date
        # self.promotion_threshold = habit.promotion_threshold
        self.created_at_local = habit.created_at_local
        self.subtype = habit.subtype
        self._tz = tz

    @property
    def status_label(self) -> str:
        return f"{self.status.title()}" if self.status else ""

    @property
    def created_at_label(self) -> str:
        return self.format_created_at_label()

