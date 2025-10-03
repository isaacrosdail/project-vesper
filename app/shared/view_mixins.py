from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.shared.datetime.helpers import convert_to_timezone

class TimestampedViewMixin:
    def _to_local(self, dt, tz):
        return convert_to_timezone(tz, dt) if dt else None
    
    def format(self, dt, tz, fmt="%Y-%m-%d %H:%M"):
        local = self._to_local(dt, tz)
        return local.strftime(fmt) if local else ""
    
    def format_due_label(self, tz):
        if not self.due_date:
            return ""
        
        today = datetime.now(ZoneInfo(tz)).date()
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
            return self.format(self.due_date, tz, "%a")
        else:
            return self.format(self.due_date, tz, "%b %d")

    def format_created_at_label(self, tz):
        today = datetime.now(ZoneInfo(tz)).date()
        created = self.created_at.date()
        delta_days = (created - today).days

        rules = {
            -1: "Yesterday",
            0: "Today"
        }

        if delta_days in rules:
            return rules[delta_days]
        elif 2 <= delta_days <= 7:
            return self.format(self.created_at, self._tz, "%a")
        else:
            return "hiya" # TODO: fix obviously
    
    def _label(self, attr: str, fmt=str, default="--"):
        val = getattr(self, attr)
        return fmt(val) if val is not None else default
    

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