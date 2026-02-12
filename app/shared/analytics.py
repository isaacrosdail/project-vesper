
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.modules.habits.service import HabitsService
    from app.modules.time_tracking.service import TimeTrackingService

import pandas as pd

from app.modules.habits.service import create_habits_service
from app.modules.time_tracking.service import create_time_tracking_service


class AnalyticsService:
    def __init__(self, habits_service: HabitsService, time_service: TimeTrackingService) -> None:
        self.habits_service = habits_service
        self.time_service = time_service

    def correlation_method(self) -> float:
        completion_counts = self.habits_service.get_daily_completion_counts()
        time_totals = self.time_service.get_time_stuff()

        # merge the two dataframes on date and return the correlation
        # pandas' version of None is NaN: .fillna(0) takes any NaN results and replaces with 0?
        # how="outer" keeps all dates from both DataFrames
        # This means for dates with a completion but no time tracked => it'll just fill
        # duration_minutes in as 0
        merged = pd.merge(completion_counts, time_totals, on="date", how="outer").fillna(0)
        #corr = merged.corr()
        # merged.corr() computes full correlation matrix between every numeric column pair?
        #                   completion_count    duration_minutes
        # completion_count          1.0                0.73
        # duration_minutes          0.73               1.0
        # diagonal is always 1 (a col correlates perfectly with itself)

        # single num is cleaner for returning/displaying:
        corr = merged["completion_count"].corr(merged["duration_minutes"])
        import sys
        print(merged, file=sys.stderr)

        return corr



def create_analytics_service(
    session: Session, user_id: int, user_tz: str
) -> AnalyticsService:

    # build both services & return
    return AnalyticsService(
        habits_service=create_habits_service(session, user_id, user_tz),
        time_service=create_time_tracking_service(session, user_id, user_tz)
    )

