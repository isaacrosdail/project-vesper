from collections import Counter
from collections.abc import Iterable
from datetime import date, timedelta
from typing import assert_never

import app.shared.datetime_.helpers as dth
from app.modules.habits.models import (
    DatedSchedule,
    FrequencySchedule,
    Habit,
)


class StreakCalculator:
    def __init__(self, today: date):
        self.today = today

    def _scan(self, satisfied: set[date], intended: Iterable[date], head: date) -> int:
        """Returns current streak."""
        streak = 0
        for i, day in enumerate(intended):
            if day in satisfied:
                streak += 1
            elif i == 0 and day == head:
                continue
            else:
                break
        return streak

    def _best_scan(self, satisfied: set[date], intended: Iterable[date], head: date) -> int:
        """Returns best streak over all intended dates."""
        best, streak = 0, 0
        for i, day in enumerate(intended):
            if day in satisfied:
                streak += 1
            elif i == 0 and day == head:
                continue
            else:
                # instead of breaking, we'd swap best if streak > best, then keep going!
                best = max(best, streak)
                streak = 0
        return max(best, streak)

    def streak(self, habit: Habit, satisfied: set[date]) -> int:
        match habit.schedule:
            case FrequencySchedule(weekly_frequency=freq):
                # return self._weekly_scan(satisfied, freq)
                tally = Counter(dth.week_start(d) for d in satisfied)
                qualified = {monday for monday, n in tally.items() if n >= freq}
                this_monday = dth.week_start(self.today)
                first_monday = dth.week_start(habit.start_date)
                mondays = [this_monday - timedelta(weeks=i) for i in range((this_monday - first_monday).days // 7 + 1)]
                return self._scan(qualified, mondays, this_monday)
            case DatedSchedule() as s:
                return self._scan(satisfied, s.intended_dates(habit.start_date, self.today), self.today)
            case _:
                assert_never(habit.schedule)

    def streaks(self, habit: Habit, satisfied: set[date]) -> tuple[int, int]:
        """Returns (current, best) streaks."""
        match habit.schedule:
            case FrequencySchedule(weekly_frequency=freq) as s:
                tally = Counter(dth.week_start(d) for d in satisfied)
                qualified = {monday for monday, n in tally.items() if n >= freq}
                this_monday = dth.week_start(self.today)
                first_monday = dth.week_start(habit.start_date)
                mondays = [this_monday - timedelta(weeks=i) for i in range((this_monday - first_monday).days // 7 + 1)]
                best = self._best_scan(qualified, mondays, this_monday)
            case DatedSchedule() as s:
                best = self._best_scan(satisfied, s.intended_dates(habit.start_date, self.today), self.today)
            case _:
                assert_never(habit.schedule)

        current = self.streak(habit, satisfied)
        return best, current

    def days_missed(self, habit: Habit, satisfied: set[date]) -> int:
        match habit.schedule:
            case DatedSchedule() as s:
                yesterday = self.today - timedelta(days=1)
                return sum(
                    1 for d in s.intended_dates(habit.start_date, yesterday)
                    if d not in satisfied
                )
            case FrequencySchedule(weekly_frequency=freq):
                this_monday = dth.week_start(self.today)
                complete_weeks = (this_monday - dth.week_start(habit.start_date)).days // 7
                completed = sum(1 for d in satisfied if d < this_monday)
                return max(0, freq * complete_weeks - completed)
            case _:
                assert_never(habit.schedule)
