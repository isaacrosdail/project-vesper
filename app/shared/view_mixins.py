from datetime import datetime, timedelta
from typing import Any, ClassVar
from zoneinfo import ZoneInfo


class BaseViewModel:
    """Adds datetime-related conversion & formatting methods to inheriting classes."""

    WEEK_CUTOFF = 7
    SOON_START = 2

    _tz: str
    created_at_local: datetime
    updated_at_local: datetime
    due_date: datetime | None

    def format_created_at_label(self) -> str:
        today = datetime.now(ZoneInfo(self._tz)).date()
        created_local = self.created_at_local.date()
        delta_days = (created_local - today).days

        rules = {-1: "Yesterday", 0: "Today"}

        if delta_days in rules:
            return rules[delta_days]
        if self.SOON_START <= delta_days <= self.WEEK_CUTOFF:
            return self.created_at_local.strftime("%a")
        else:
            return self.created_at_local.strftime("%b %d")


class HasDueDateMixin:
    WEEK_CUTOFF = 7
    SOON_START = 2

    due_date_local: datetime | None
    _tz: str

    def format_due_label(self) -> str:
        if not self.due_date_local:
            return ""

        today = datetime.now(ZoneInfo(self._tz)).date()
        # Stored at exclusive EOD (ie 00:00 next day), so timedelta -1 second to adjust
        due = (self.due_date_local - timedelta(seconds=1)).date()
        delta_days = (due - today).days

        rules = {-1: "Yesterday", 0: "Today", 1: "Tomorrow"}

        if delta_days in rules:
            return rules[delta_days]
        if self.SOON_START <= delta_days < self.WEEK_CUTOFF:
            return self.due_date_local.strftime("%a")
        else:
            return self.due_date_local.strftime("%b %d")


class BasePresenter:
    VISIBLE_COLUMNS: ClassVar[list[str]] = []
    COLUMN_CONFIG: ClassVar[dict[str, dict[str, Any]]] = {}

    @classmethod
    def build_columns(cls) -> list[dict[str, Any]]:
        """
        Builds a list of column definitions for use as table headers.
        Respects order defined in `VISIBLE_COLUMNS`.
        Excludes fields not explicitly whitelisted.

        Note: `sort_field` is optional: fall back to key in macro if sort_field is missing.
        """
        return [
            {
                "key": col,
                "sort_field": cls.COLUMN_CONFIG[col].get("sort_field"),
                "label": cls.COLUMN_CONFIG[col]["label"],
                "priority": cls.COLUMN_CONFIG[col]["priority"],
            }
            for col in cls.VISIBLE_COLUMNS
        ]
