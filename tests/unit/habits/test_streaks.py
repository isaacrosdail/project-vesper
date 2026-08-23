from collections import Counter
from datetime import date, timedelta

import pytest

from app.modules.habits.models import (
    Habit,
    HabitTypeEnum,
    IntervalSchedule,
    MonthlySchedule,
    ScheduleTypeEnum,
    WeeklySchedule,
)
from app.modules.habits.streaks import StreakCalculator
import app.shared.datetime_.helpers as dth

TODAY = date(2026, 8, 19)  # a Wednesday; Mon = 2026-08-17

MWF = [1, 3, 5]
EVERYDAY = [1, 2, 3, 4, 5, 6, 7]


@pytest.fixture
def calc() -> StreakCalculator:
    return StreakCalculator(today=TODAY)

def thing(satisfied, freq, start_date):
    tally = Counter(dth.week_start(d) for d in satisfied)
    qualified = {monday for monday, n in tally.items() if n >= freq}
    this_monday = dth.week_start(TODAY)
    first_monday = dth.week_start(start_date)
    mondays = [this_monday - timedelta(weeks=i) for i in range((this_monday - first_monday).days // 7 + 1)]
    return qualified, mondays, this_monday


# --- generators -------------------------------------------------------------

def test_gen_weekly_dates(calc):
    res = list(WeeklySchedule(scheduled_days=MWF).intended_dates(date(2026, 8, 10), TODAY))
    assert res == [date(2026, 8, 19), date(2026, 8, 17),
                   date(2026, 8, 14), date(2026, 8, 12), date(2026, 8, 10)]

def test_gen_interval_dates_snaps_off_grid_today():
    # anchor Aug 1, N=3 -> grid 1, 4, 7, 10, 13, 16, 19; today Aug 20 is off-grid
    res = list(IntervalSchedule(interval_days=3).intended_dates(date(2026, 8, 13), date(2026, 8, 20)))
    assert res == [date(2026, 8, 19), date(2026, 8, 16), date(2026, 8, 13)]

def test_gen_monthly_dates_explicit_and_last(calc):
    res = list(MonthlySchedule(monthly_days=[1, -1]).intended_dates(date(2026, 6, 20), TODAY))
    assert res == [date(2026, 8, 1), date(2026, 7, 31),
                   date(2026, 7, 1), date(2026, 6, 30)]

def test_gen_monthly_dates_day_31_skips_short_months(calc):
    res = list(MonthlySchedule(monthly_days=[31]).intended_dates(date(2026, 5, 20), TODAY))
    # June has no 31st -> should be silently absent
    assert res == [date(2026, 7, 31), date(2026, 5, 31)]


# --- scheduled scan (weekly mode) -------------------------------------------

@pytest.mark.parametrize(("dates", "expected"), [
    (set(), 0),
    # Mon 17 + Wed 19 (today) satisfied, Fri 14 missing stops the walk
    ({date(2026, 8, 17), date(2026, 8, 19)}, 2),
    # today intended but not done yet -> skipped without breaking
    ({date(2026, 8, 17)}, 1),
    ({date(2026, 8, 19)}, 1),
    ({date(2026, 8, 14), date(2026, 8, 17), date(2026, 8, 19)}, 3),
    # completion on a non-intended day (Tue 18) has no effect
    ({date(2026, 8, 18)}, 0),
    # dead streak from earlier in the month
    ({date(2026, 8, 3), date(2026, 8, 5)}, 0),
])
def test_scan_scheduled_mwf(calc, dates, expected):
    intended = WeeklySchedule(scheduled_days=MWF).intended_dates(date(2026, 8, 1), TODAY)
    assert calc._scan(dates, intended, TODAY) == expected


def test_scan_everyday_matches_old_daily_semantics(calc):
    # Mon 17 + Tue 18 done, today (Wed) in-progress -> 2
    intended = WeeklySchedule(scheduled_days=EVERYDAY).intended_dates(date(2026, 8, 1), TODAY)
    assert calc._scan({date(2026, 8, 17), date(2026, 8, 18)}, intended, TODAY) == 2


# --- interval scan ----------------------------------------------------------

@pytest.mark.parametrize(("dates", "expected"), [
    (set(), 0),
    # grid (anchor Aug 1, N=3): ... 13, 16, 19(today)
    ({date(2026, 8, 16), date(2026, 8, 19)}, 2),
    # today's grid day in-progress: skipped without breaking
    ({date(2026, 8, 13), date(2026, 8, 16)}, 2),
    # off-grid completion has no effect
    ({date(2026, 8, 15)}, 0),
    # gap in the grid stops the walk
    ({date(2026, 8, 10), date(2026, 8, 16), date(2026, 8, 19)}, 2),
])
def test_scan_interval(calc, dates, expected):
    intended = IntervalSchedule(interval_days=3).intended_dates(date(2026, 8, 1), TODAY)
    assert calc._scan(dates, intended, TODAY) == expected


# --- monthly scan -----------------------------------------------------------

def test_scan_monthly_counts_occurrences(calc):
    intended = MonthlySchedule(monthly_days=[1]).intended_dates(date(2026, 6, 1), TODAY)
    assert calc._scan({date(2026, 8, 1), date(2026, 7, 1)}, intended, TODAY) == 2


def test_scan_monthly_dead_occurrence_no_grace(calc):
    # Aug 1 already elapsed and missed -> dead; grace only covers today itself
    intended = MonthlySchedule(monthly_days=[1]).intended_dates(date(2026, 6, 1), TODAY)
    assert calc._scan({date(2026, 7, 1), date(2026, 6, 1)}, intended, TODAY) == 0


def test_scan_monthly_grace_when_todays_occurrence_pending():
    calc = StreakCalculator(today=date(2026, 8, 1))
    intended = MonthlySchedule(monthly_days=[1]).intended_dates(date(2026, 7, 1), date(2026, 8, 1))
    assert calc._scan({date(2026, 7, 1)}, intended, TODAY) == 1


# --- frequency mode (weeks) -------------------------------------------------

def test_weekly_scan_counts_qualifying_weeks(calc):
    satisfied = {
        date(2026, 8, 17), date(2026, 8, 18),   # this week: 2 -> qualifies
        date(2026, 8, 10), date(2026, 8, 13),   # last week: 2 -> qualifies
    }
    # assert calc._weekly_scan(dates, 2) == 2
    start_date = date(2026, 8, 10)
    assert calc._scan(*thing(satisfied, 2, start_date)) == 2


def test_weekly_scan_this_week_pending_keeps_streak(calc):
    # this week only 1 so far, last week qualified -> streak lives at 1
    satisfied = {date(2026, 8, 17), date(2026, 8, 10), date(2026, 8, 13)}
    start_date = date(2026, 8, 9)
    assert calc._scan(*thing(satisfied, 2, start_date)) == 1


def test_weekly_scan_dead_streak_is_zero(calc):
    # 3 qualifying weeks in June, nothing since -> 0 (anchor check)
    satisfied = {
        date(2026, 6, 1), date(2026, 6, 2),
        date(2026, 6, 8), date(2026, 6, 9),
        date(2026, 6, 15), date(2026, 6, 16),
    }
    start_date = date(2026, 6, 1)
    assert calc._scan(*thing(satisfied, 2, start_date)) == 0


# --- dispatch through Habit.schedule ----------------------------------------

def _habit(**kwargs) -> Habit:
    return Habit(
        name="t", type=HabitTypeEnum.BINARY,
        start_date=date(2026, 8, 1), **kwargs,
    )


@pytest.mark.parametrize(("habit", "dates", "expected"), [
    (_habit(schedule_type=ScheduleTypeEnum.WEEKLY, scheduled_days=MWF),
     {date(2026, 8, 17), date(2026, 8, 19)}, 2),
    (_habit(schedule_type=ScheduleTypeEnum.INTERVAL, interval_days=3),
     {date(2026, 8, 16), date(2026, 8, 19)}, 2),
    # start_date Aug 1 bounds the walk: Jul 1 is before the habit existed
    (_habit(schedule_type=ScheduleTypeEnum.MONTHLY, monthly_days=[1]),
     {date(2026, 8, 1), date(2026, 7, 1)}, 1),
    (_habit(schedule_type=ScheduleTypeEnum.FREQUENCY, weekly_frequency=2),
     {date(2026, 8, 17), date(2026, 8, 18)}, 1),
])
def test_streak_dispatch(calc, habit, dates, expected):
    assert calc.streak(habit, dates) == expected
