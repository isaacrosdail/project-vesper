from collections import Counter
from collections.abc import Iterable
from datetime import date, timedelta
from itertools import pairwise
from typing import assert_never

import app.shared.datetime_.helpers as dth
from app.modules.habits.models import (
    FrequencySchedule,
    Habit,
    IntervalSchedule,
    MonthlySchedule,
    WeeklySchedule,
)


class StreakCalculator:
    def __init__(self, today: date):
        self.today = today

    def _scan(self, satisfied: set[date], intended: Iterable[date]) -> int:
        streak = 0
        for i, day in enumerate(intended):
            if day in satisfied:
                streak += 1
            elif i == 0 and day == self.today:
                continue
            else:
                break
        return streak

    def streak(self, habit: Habit, satisfied_dates: set[date]) -> int:
        match habit.schedule:
            case IntervalSchedule(interval_days=interval_days):
                return self._scan(satisfied_dates, habit.schedule.intended_dates(habit.start_date, self.today))
            case WeeklySchedule(scheduled_days=sd):
                return self._scan(satisfied_dates, habit.schedule.intended_dates(habit.start_date, self.today))
            case MonthlySchedule(monthly_days=md):
                return self._scan(satisfied_dates, habit.schedule.intended_dates(habit.start_date, self.today))
            case FrequencySchedule(weekly_frequency=freq):
                return self._weekly_scan(satisfied_dates, freq)
            case _:
                assert_never(habit.schedule)

    def _weekly_scan(self, dates: set[date], weekly_frequency: int) -> int:
        if not dates:
            return 0

        # head week is this week or last week
        # Get per-week tallies with weeks anchored on Mondays
        # in: [Jan 9, Jan 8, Jan 6] --> out: {Jan 5: 3}
        tally = Counter(dth.week_start(d) for d in dates)
        # Keep only weeks that hit weekly_frequency
        filtered: list[date] = sorted([k for k, v in tally.items() if v >= weekly_frequency], reverse=True)

        # Anchor check
        # filtered[0] is this week OR last week's monday
        this_monday = dth.week_start(self.today)
        if len(filtered) == 0 or filtered[0] not in (this_monday, this_monday - timedelta(days=7)):
            return 0

        streak = 1
        for curr, prev in pairwise(filtered):
            if (curr - prev).days == 7:
                streak += 1
            else:
                break
        return streak



