
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from app.modules.habits.models import Habit, LeetCodeRecord

from app.shared.view_mixins import BasePresenter, TimestampedViewMixin


class HabitPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "name", "status", "created_at"
    ]
    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "name": {"label": "Name", "priority": "essential"},
        "tags": {"label": "Tag(s)", "priority": "desktop-only"},
        "status": {"label": "Status", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "established_date": {"label": "Date Promoted", "priority": "desktop-only"},
        "promotion_threshold": {"label": "Promotion Threshold", "priority": "desktop-only"}
    }


class HabitViewModel(TimestampedViewMixin):
    def __init__(self, habit: Habit, tz: str) -> None:
        self.id = habit.id
        self.name = habit.name
        self.status = habit.status
        self.established_date = habit.established_date
        self.promotion_threshold = habit.promotion_threshold
        self.created_at = habit.created_at
        self._tz = tz

    @property
    def status_label(self) -> str:
        return f"{self.status.value.title()}"

    @property
    def created_at_label(self) -> str:
        return self.format_created_at_label()


class LCRecordPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "leetcode_id", "title", "difficulty", "language", "status"
    ]

    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "ID", "priority": "essential"},
        "leetcode_id": {"label": "Leetcode ID", "priority": "essential"},
        "title": {"label": "Title", "priority": "essential"},
        "difficulty": {"label": "Difficulty", "priority": "essential"},
        "language": {"label": "Language", "priority": "essential"},
        "status": {"label": "Status", "priority": "essential"},
    }

class LCRecordViewModel(TimestampedViewMixin):
    def __init__(self, record: LeetCodeRecord, tz: str) -> None:
        self.id = record.id
        self.leetcode_id = record.leetcode_id
        self.title = record.title
        self.difficulty = record.difficulty
        self.language = record.language
        self.status = record.status
        self._tz = tz

    @property
    def title_label(self) -> str:
        return f"{self.title}" if self.title else "--"

    @property
    def difficulty_label(self) -> str:
        return f"{self.difficulty.value.title()}"

    @property
    def language_label(self) -> str:
        return f"{self.language.value.title()}"

    @property
    def status_label(self) -> str:
        return f"{self.status.value.title()}"
