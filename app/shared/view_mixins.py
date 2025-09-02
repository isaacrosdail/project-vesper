from app.shared.datetime.helpers import convert_to_timezone

class TimestampedViewMixin:
    def _to_local(self, dt, tz):
        return convert_to_timezone(tz, dt) if dt else None
    
    def format(self, dt, tz, fmt="%Y-%m-%d %H:%M"):
        local = self._to_local(dt, tz)
        return local.strftime(fmt) if local else ""
    

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