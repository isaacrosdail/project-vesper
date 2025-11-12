from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from app.modules.metrics.models import ABTest, ABTrial, DailyEntry
from app.shared.repository.base import BaseRepository


class DailyMetricsRepository(BaseRepository[DailyEntry]):
    def __init__(self, session: 'Session', user_id: int, user_tz: str):
        super().__init__(session, user_id, user_tz, model_cls=DailyEntry)

    def create_daily_metric(
            self,
            entry_datetime: datetime,
            weight: Decimal | None = None,
            steps: int | None = None,
            wake_time: datetime | None = None,
            sleep_time: datetime | None = None,
            sleep_duration_minutes: int | None = None,
            calories: int | None = None,
    ) -> DailyEntry:
        """Create & add a new daily metric. Returns metric."""
        entry = DailyEntry(
            user_id=self.user_id,
            entry_datetime=entry_datetime,
            weight=weight,
            steps=steps,
            wake_time=wake_time,
            sleep_time=sleep_time,
            sleep_duration_minutes=sleep_duration_minutes,
            calories=calories,
        )
        return self.add(entry)

    def get_daily_metric_in_window(self, start_utc: datetime, end_utc: datetime) -> DailyEntry | None:
        """Returns the first DailyEntry in a UTC datetime range."""
        stmt = self._user_select(DailyEntry).where(
            DailyEntry.entry_datetime >= start_utc,
            DailyEntry.entry_datetime < end_utc
        )
        result = self.session.execute(stmt).scalars().first()
        return cast(DailyEntry | None, result)
    
    def get_all_metrics_in_window(self, start_utc: datetime, end_utc: datetime) -> list[DailyEntry]:
        """Returns the first DailyEntry in a UTC datetime range."""
        stmt = self._user_select(DailyEntry).where(
            DailyEntry.entry_datetime >= start_utc,
            DailyEntry.entry_datetime < end_utc
        )
        result = self.session.execute(stmt).scalars().all()
        return list(result)

    def get_metrics_by_type_in_window(self, metric_type: str, start_utc: datetime, end_utc: datetime) -> list[Any]:
        """Returns list of (entry_datetime, <metric_value>) tuples for a given metric type."""
        column_obj = getattr(DailyEntry, metric_type)
        
        stmt = select(DailyEntry.entry_datetime, column_obj).where(
            DailyEntry.user_id == self.user_id,
            DailyEntry.entry_datetime >= start_utc,
            DailyEntry.entry_datetime < end_utc,
            column_obj.isnot(None),
        ).order_by(DailyEntry.entry_datetime)

        # Note: We don't need .scalars() here since we're intentionally selecting multiple fields
        return list(self.session.execute(stmt).all())
    

class ABTestRepository(BaseRepository[ABTest]):
    def __init__(self, session: 'Session', user_id: int, user_tz: str):
        super().__init__(session, user_id, user_tz, model_cls=ABTest)

    def create_abtest(
            self,
            title: str,
            hypothesis: str,
            variant_a_label: str,
            variant_b_label: str,
            success_condition: str
    ) -> ABTest:
        abtest = ABTest(
            user_id=self.user_id,
            title=title,
            hypothesis=hypothesis,
            variant_a_label=variant_a_label,
            variant_b_label=variant_b_label,
            success_condition=success_condition
        )
        return self.add(abtest)
    
class ABTrialRepository(BaseRepository[ABTrial]):
    def __init__(self, session: 'Session', user_id: int, user_tz: str):
        super().__init__(session, user_id, user_tz, model_cls=ABTrial)

    def create_abtrial(
            self,
            abtest_id: int,
            variant: str,
            is_success: bool,
            notes: str
    ) -> ABTrial:
        abtrial = ABTrial(
            user_id=self.user_id,
            abtest_id=abtest_id,
            variant=variant,
            is_success=is_success,
            notes=notes
        )
        return self.add(abtrial)