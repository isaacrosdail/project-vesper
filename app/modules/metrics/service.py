from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.modules.metrics.repository import DailyMetricsRepository
from app.shared.datetime.helpers import today_range_utc, parse_time_to_datetime
from app.modules.api.responses import service_response


class DailyMetricsService:
    def __init__(self, repository: DailyMetricsRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def process_daily_metrics(self, form_data: dict) -> dict:
        start_utc, end_utc = today_range_utc(self.user_tz)
        processed_metrics = []

        # Iterate over key-value pairs, calling create/update for each whose value is a non-empty string (which is falsy in Python)
        for metric_type, value in form_data.items():
            if value:
                processed_value = self._process_metric_value(metric_type, value)

                metric, was_created = self.repo.create_or_update_daily_metric(metric_type, processed_value, start_utc, end_utc)
                processed_metrics.append({"metric_type": metric_type, "created": was_created })
        
        return service_response(
            True,
            f"Added {len(processed_metrics)} metrics",
            data = {"metrics": processed_metrics}
        )
    
    def _process_metric_value(self, metric_type: str, value: str):
        if metric_type == "wake_time":
            today = datetime.now(ZoneInfo(self.user_tz)).date()
            return parse_time_to_datetime(value, today, self.user_tz)
        elif metric_type == "sleep_time":
            yesterday = (datetime.now(ZoneInfo(self.user_tz)) - timedelta(days=1)).date()
            return parse_time_to_datetime(value, yesterday, self.user_tz)
        else:
            return value # pass through as-is for other metrics