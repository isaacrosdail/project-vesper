from datetime import date

import pytest

from app.modules.habits.models import HabitTypeEnum
import app.shared.datetime_.helpers as dth
from app.modules.habits.schemas import BinaryHabitCreate
from app.modules.habits.service import create_habits_service

# Wednesday; Mon = 2026-08-17, week = Aug 17-23
PINNED_TODAY = date(2026, 8, 19)


@pytest.fixture
def svc(session, logged_in_user, monkeypatch):
    monkeypatch.setattr(dth, "user_today", lambda tz: PINNED_TODAY)
    return create_habits_service(session, logged_in_user.id, logged_in_user.timezone)


def _make_habit(svc, **fields):
    fields.setdefault("start_date", date(2026, 8, 1))
    fields.setdefault("name", f"h-{fields['schedule_type']}")
    validated = BinaryHabitCreate(type=HabitTypeEnum.BINARY, **fields)
    return svc.create_habit(validated)


def _complete(svc, habit_id: int, *dates: date) -> None:
    for d in dates:
        svc.completion_repo.create_habit_completion(habit_id, d)


def test_week_progress_weekly_mode_counts_only_intended_days(svc):
    # MWF habit; Mon + Tue + Wed logged -> Tue is inert, so 2 of 3
    h = _make_habit(svc, schedule_type="weekly", scheduled_days=[1, 3, 5])
    _complete(svc, h.id, date(2026, 8, 17), date(2026, 8, 18), date(2026, 8, 19))

    result = svc.calculate_all_habits_percentage_this_week()

    assert result == {"completed": 2, "total": 3, "percent": 67}


def test_week_progress_frequency_mode_caps_at_frequency(svc):
    # 2/wk habit; 3 satisfied days -> capped at 2 of 2
    h = _make_habit(svc, schedule_type="frequency", weekly_frequency=2)
    _complete(svc, h.id, date(2026, 8, 17), date(2026, 8, 18), date(2026, 8, 19))

    result = svc.calculate_all_habits_percentage_this_week()

    assert result == {"completed": 2, "total": 2, "percent": 100}


def test_week_progress_start_date_bounds_expected(svc):
    # MWF habit that only starts this Friday: Mon/Wed aren't intended yet
    _make_habit(svc, schedule_type="weekly", scheduled_days=[1, 3, 5],
                start_date=date(2026, 8, 21))
    result = svc.calculate_all_habits_percentage_this_week()

    assert result["total"] == 1  # Friday the 21st only
    assert result["completed"] == 0


def test_week_progress_sums_across_modes(svc):
    mwf = _make_habit(svc, schedule_type="weekly", scheduled_days=[1, 3, 5])
    freq = _make_habit(svc, schedule_type="frequency", weekly_frequency=2)
    _complete(svc, mwf.id, date(2026, 8, 17))
    _complete(svc, freq.id, date(2026, 8, 18))

    result = svc.calculate_all_habits_percentage_this_week()

    # mwf: 1/3, freq: 1/2 -> 2/5
    assert result == {"completed": 2, "total": 5, "percent": 40}


def test_consistency_clamps_to_start_date(svc):
    # 4-week window is [Jul 20, Aug 17); habit starts Aug 10 mid-window.
    # MWF intended dates from start: Aug 10, 12, 14 -> expected 3; 2 satisfied.
    h = _make_habit(svc, schedule_type="weekly", scheduled_days=[1, 3, 5],
                    start_date=date(2026, 8, 10))
    _complete(svc, h.id, date(2026, 8, 10), date(2026, 8, 12))

    assert svc.calc_consistency_all()[h.id] == 67


def test_week_progress_no_habits(svc):
    assert svc.calculate_all_habits_percentage_this_week() == {
        "completed": 0, "total": 0, "percent": 0,
    }
