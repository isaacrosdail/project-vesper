from app.shared.datetime.helpers import convert_to_timezone

class TimestampedViewMixin:
    def _to_local(self, dt, tz):
        return convert_to_timezone(tz, dt) if dt else None
    
    def format(self, dt, tz, fmt="%Y-%m-%d %H:%M"):
        local = self._to_local(dt, tz)
        return local.strftime(fmt) if local else ""