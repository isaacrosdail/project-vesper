
from app.shared.view_mixins import TimestampedViewMixin

class DailyMetricPresenter:
    VISIBLE_COLUMNS = [
        "created_at", "weight", "steps", "wake_time", "sleep_time", "calories"
    ]
    
    COLUMN_LABELS = {
        "created_at": "Created",
        "updated_at": "Last Updated",
        "weight": "Weight",
        "steps": "Steps",
        "wake_time": "Wake Time",
        "sleep_time": "Sleep Time",
        "calories": "Calories"
    }

    @classmethod
    def build_columns(cls) -> list[dict]:
        """
        Builds a list of column definitions for use as table headers.
        Respects the order defined in `VISIBLE_COLUMNS` & excludes fields not explicitly whitelisted.
        """
        return [{"key": c, "label": cls.COLUMN_LABELS.get(c, c)} for c in cls.VISIBLE_COLUMNS]

class DailyMetricViewModel(TimestampedViewMixin):
    def __init__(self, metric, tz):
        self.id = metric.id
        self.created_at = metric.created_at
        self.weight = metric.weight
        self.steps = metric.steps
        self.wake_time = metric.wake_time
        self.sleep_time = metric.sleep_time
        self.calories = metric.calories
        self._tz = tz

    # Perhaps options for 24H vs 12H time displays based on user prefs?
    @property
    def created_at_local(self):
        return self._to_local(self.created_at, self._tz)
    
    @property
    def created_at_label(self):
        return self.format(self.created_at, self._tz, "%I:%M %p")
    
    @property
    def weight_label(self):
        return f"{self.weight:.2f}" if self.weight else "--"
    
    @property
    def wake_time_label(self):
        return f"{self.wake_time}" if self.wake_time is not None else "--"
    
    @property
    def sleep_time_label(self):
        return f"{self.sleep_time}" if self.sleep_time is not None else "--"
    
    @property
    def calories_label(self):
        return f"{self.calories}" if self.calories is not None else "--"