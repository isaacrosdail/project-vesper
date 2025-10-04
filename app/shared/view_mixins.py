from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.shared.datetime.helpers import convert_to_timezone

class TimestampedViewMixin:
    """Adds datetime-related conversion & formatting methods to inheriting classes."""

    def format_dt(self, dt, fmt="%Y-%m-%d %H:%M"):
        """Format datetime in user's timezone."""
        local = convert_to_timezone(self._tz, dt)
        return local.strftime(fmt)

    def format_due_label(self):
        if not self.due_date:
            return ""
        
        today = datetime.now(ZoneInfo(self._tz)).date()
        # Stored at exclusive EOD (ie 00:00 next day), so timedelta -1 second to adjust
        due = (self.due_date - timedelta(seconds=1)).date()
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

    def format_created_at_label(self):
        today = datetime.now(ZoneInfo(self._tz)).date()
        created = self.created_at.date()
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
    @classmethod
    def build_columns(cls) -> list[dict]:
        """
        Builds a list of column definitions for use as table headers.
        Respects the order defined in `VISIBLE_COLUMNS` & excludes fields not explicitly whitelisted.
        """
        return [
            {
                "key": col, 
                "label": cls.COLUMN_CONFIG[col]["label"],
                "priority": cls.COLUMN_CONFIG[col]["priority"]
            }
            for col in cls.VISIBLE_COLUMNS]