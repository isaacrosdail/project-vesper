from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.constants import WAKE_MUST_BE_AFTER_SLEEP
from app.shared.datetime.helpers import today_range_utc, parse_time_to_datetime
from app.modules.api.responses import service_response


class DailyMetricsService:
    def __init__(self, repository: DailyMetricsRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def process_daily_metrics(self, metric_data: dict) -> dict:
        start_utc, end_utc = today_range_utc(self.user_tz)
        processed_metrics = []

        # Check wake/sleep times are sensible
        if "wake_time" in metric_data and "sleep_time" in metric_data:
            wake_dt = self._convert_time_to_datetime("wake_time", metric_data["wake_time"])
            sleep_dt = self._convert_time_to_datetime("sleep_time", metric_data["sleep_time"])

            if wake_dt <= sleep_dt:
                return service_response(
                    False,
                    "Wake/Sleep time check failed",
                    errors={
                        "wake_time": [WAKE_MUST_BE_AFTER_SLEEP],
                        "sleep_time": [WAKE_MUST_BE_AFTER_SLEEP]
                    }
                )

        for metric_type, value in metric_data.items():

            if metric_type in ("wake_time", "sleep_time"):
                value = self._convert_time_to_datetime(metric_type, value)

            metric, was_created = self.repo.create_or_update_daily_metric(
                metric_type, value, start_utc, end_utc
            )
            processed_metrics.append({"metric_type": metric_type, "created": was_created })
        
        return service_response(
            True,
            f"Added {len(processed_metrics)} metrics",
            data = {"metrics": processed_metrics}
        )
    
    def _convert_time_to_datetime(self, metric_type: str, value: str) -> datetime:
        if metric_type == "wake_time":
            today = datetime.now(ZoneInfo(self.user_tz)).date()
            return parse_time_to_datetime(value, today, self.user_tz)
        else:
            yesterday = (datetime.now(ZoneInfo(self.user_tz)) - timedelta(days=1)).date()
            return parse_time_to_datetime(value, yesterday, self.user_tz)