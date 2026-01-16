
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.shared.datetime.helpers import convert_to_timezone

class HasTimestampedFields(Protocol):
    _tz: str
    created_at: datetime
    updated_at: datetime
    due_date: datetime | None

    def format_dt(self, dt: datetime, fmt: str = "%Y-%m-%d %H:%M") -> str: ...
    def format_created_at_label(self) -> str | datetime: ...


class TimestampedViewMixin:
    """Adds datetime-related conversion & formatting methods to inheriting classes."""

    if TYPE_CHECKING: # TODO: TEMP! Need better solution
        _tz: str
        created_at: datetime
        updated_at: datetime
        due_date: datetime | None

    def format_dt(self, dt: datetime, fmt: str ="%Y-%m-%d %H:%M") -> str:
        """Format datetime in user's timezone."""
        local = convert_to_timezone(self._tz, dt)
        return local.strftime(fmt)

    def format_due_label(self) -> str:
        if not self.due_date:
            return ""

        today = datetime.now(ZoneInfo(self._tz)).date()
        # Stored at exclusive EOD (ie 00:00 next day), so timedelta -1 second to adjust
        due_local = convert_to_timezone(self._tz, self.due_date)
        due = (due_local - timedelta(seconds=1)).date()
        delta_days = (due - today).days

        rules = {
            -1: "Yesterday",
            0: "Today",
            1: "Tomorrow"
        }

        if delta_days in rules:
            return rules[delta_days]
        elif 2 <= delta_days < 7:
            return self.format_dt(self.due_date, "%a")
        else:
            return self.format_dt(self.due_date, "%b %d")

    def format_created_at_label(self) -> str:
        today = datetime.now(ZoneInfo(self._tz)).date()
        created = (convert_to_timezone(self._tz, self.created_at)).date()
        delta_days = (created - today).days

        rules = {
            -1: "Yesterday",
            0: "Today"
        }

        if delta_days in rules:
            return rules[delta_days]
        elif 2 <= delta_days <= 7:
            return self.format_dt(self.created_at, "%a")
        else:
            return self.format_dt(self.created_at, "%b %d")
    

    

class BasePresenter:
    VISIBLE_COLUMNS: ClassVar[list[str]] = []
    COLUMN_CONFIG: ClassVar[dict[str, dict[str, Any]]] = {}

    @classmethod
    def build_columns(cls) -> list[dict[str, Any]]:
        """
        Builds a list of column definitions for use as table headers.
        Respects the order defined in `VISIBLE_COLUMNS` & excludes fields not explicitly whitelisted.
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
