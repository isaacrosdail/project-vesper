
from app.shared.view_mixins import TimestampedViewMixin, BasePresenter

class DailyMetricPresenter(BasePresenter):
    VISIBLE_COLUMNS = [
        "created_at", "weight", "steps", "wake_time", "sleep_time", "calories"
    ]
    
    COLUMN_CONFIG = {
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "updated_at": {"label": "Last Updated", "priority": "desktop-only"},
        "weight": {"label": "Weight", "priority": "essential"},
        "steps": {"label": "Steps", "priority": "essential"},
        "wake_time": {"label": "Wake Time", "priority": "essential"},
        "sleep_time": {"label": "Sleep Time", "priority": "essential"},
        "calories": {"label": "Calories", "priority": "essential"}
    }


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