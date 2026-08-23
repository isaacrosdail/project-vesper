import pytest
from pydantic import ValidationError

from app.modules.habits.schemas import BinaryHabitCreate, HabitPatch


@pytest.mark.parametrize(("payload", "ok"), [
    ({"schedule_type": "frequency", "weekly_frequency": 3}, True),
    ({"schedule_type": "frequency"}, False),                          # mode without its param
    ({"schedule_type": "weekly", "scheduled_days": [1, 3, 5]}, True),
    ({"schedule_type": "weekly", "scheduled_days": [1, 2, 3, 4, 5, 6, 7]}, True),  # everyday
    ({"schedule_type": "weekly", "weekly_frequency": 3}, False),      # wrong param
    ({"schedule_type": "weekly", "scheduled_days": []}, False),       # empty array
    ({"schedule_type": "weekly", "scheduled_days": [0, 3]}, False),   # out of range
    ({"schedule_type": "frequency", "weekly_frequency": 3,
      "scheduled_days": [1]}, False),                                 # extra
    ({"schedule_type": "monthly", "monthly_days": [1, 29, -1]}, True),
    ({"schedule_type": "monthly", "monthly_days": [0]}, False),
    ({"schedule_type": "monthly", "monthly_days": [32]}, False),
    ({"schedule_type": "interval", "interval_days": 2}, True),
    ({"schedule_type": "interval", "interval_days": 0}, False),
])
def test_schedule_shapes(payload, ok):
    data = {"name": "Test", "type": "binary", **payload}
    if ok:
        BinaryHabitCreate(**data)
    else:
        with pytest.raises(ValidationError):
            BinaryHabitCreate(**data)


def test_scheduled_days_sorted_and_deduped():
    habit = BinaryHabitCreate(
        name="Test", type="binary",
        schedule_type="weekly", scheduled_days=[5, 1, 5, 3],
    )
    assert habit.scheduled_days == [1, 3, 5]


@pytest.mark.parametrize(("payload", "ok"), [
    ({}, True),                                                       # empty patch is legal
    ({"name": "Renamed"}, True),
    ({"schedule_type": "weekly", "scheduled_days": [1, 2]}, True),    # mode switch, full pair
    ({"schedule_type": "interval", "interval_days": 3}, True),
    ({"scheduled_days": [1]}, False),                                 # param without mode
    ({"schedule_type": "weekly"}, False),                             # mode without param
    ({"schedule_type": "weekly", "interval_days": 3}, False),         # mismatched pair
    ({"name": None}, False),                                          # explicit null on required field
])
def test_patch_schedule_shapes(payload, ok):
    if ok:
        HabitPatch(**payload)
    else:
        with pytest.raises(ValidationError):
            HabitPatch(**payload)


@pytest.mark.parametrize(("start", "end", "ok"), [
    ("2026-08-01", "2026-08-20", True),
    ("2026-08-20", "2026-08-20", True),   # one-day habit is legal
    ("2026-08-20", "2026-08-01", False),  # end before start
])
def test_end_date_not_before_start_date(start, end, ok):
    data = {
        "name": "Test", "type": "binary",
        "schedule_type": "frequency", "weekly_frequency": 3,
        "start_date": start, "end_date": end,
    }
    if ok:
        BinaryHabitCreate(**data)
    else:
        with pytest.raises(ValidationError):
            BinaryHabitCreate(**data)
