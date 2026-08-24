from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from app._infra.database import db_session
from app.modules.metrics.models import WeightUnitsEnum
from app.modules.metrics.schemas import DailyMetricsCreate
from app.modules.metrics.service import create_metrics_service

TZ = "America/Chicago"
@pytest.fixture
def metrics_service(logged_in_user):
    return create_metrics_service(db_session, user_id=logged_in_user.id, user_tz=TZ)


def metrics_payload(**overrides: dict[str, int | str]) -> dict:
    return {
        "entry_date": "2026-07-09",
        "steps": 8000,
        "calories": 2100,
        "weight": 70,
        "weight_units": WeightUnitsEnum.KG,
        "sleep_datetime": "2026-07-09T01:00:00Z",
        "wake_datetime": "2026-07-09T08:30:00Z",
    } | overrides


def test_save_daily_metrics_creates_full_entry(metrics_service):
    validated = DailyMetricsCreate(**metrics_payload())

    entry, is_new = metrics_service.save_daily_metrics(validated, entry_id=None)

    assert is_new is True
    assert entry.id is not None
    assert entry.steps == 8000
    assert entry.calories == 2100
    assert entry.weight == 70
    assert entry.entry_datetime == datetime(2026, 7, 9, 0, 0, tzinfo=ZoneInfo(TZ))
    assert entry.sleep_duration_minutes == 450


def test_save_daily_metrics_change_sleep(metrics_service):
    validated = DailyMetricsCreate(**metrics_payload(wake_datetime=None))

    entry, is_new = metrics_service.save_daily_metrics(validated, entry_id=None)

    assert is_new
    assert entry.wake_datetime is None

    validated_two = DailyMetricsCreate(entry_date="2026-07-09", wake_datetime="2026-07-09T08:30:00Z")
    entry, is_new = metrics_service.save_daily_metrics(validated_two, entry_id=entry.id)

    assert is_new is False
    assert entry.sleep_datetime == datetime(2026, 7, 9, 1, 0, tzinfo=ZoneInfo(TZ))
    assert entry.sleep_duration_minutes == 450 # duration now computable



# form pre-populated with units matching user prefs
# but can be overriden
# sending either units or weight without the other -> validation error
def test_save_daily_metrics_both_weight_and_units_required():
    units_without_weight = {
        "entry_date": "2026-07-09",
        "weight_units": "lbs",
    }
    with pytest.raises(ValidationError, match="Weight entry requires accompanying weight_units value"):
        DailyMetricsCreate(**units_without_weight)


def test_save_daily_metrics_weight_converts(metrics_service):
    my_dict = {
        "entry_date": "2026-07-09",
        "weight_units": "lbs",
        "weight": 110,
    }

    validated = DailyMetricsCreate(**my_dict)
    entry, _ = metrics_service.save_daily_metrics(validated, entry_id=None)

    assert entry.weight == pytest.approx(49.9, abs=0.01)


def test_upsert_same_date_merges(metrics_service):
    first = DailyMetricsCreate(**metrics_payload())
    entry, is_new = metrics_service.save_daily_metrics(first, entry_id=None)
    assert is_new

    second = DailyMetricsCreate(entry_date="2026-07-09", steps=12000)
    merged, is_new = metrics_service.save_daily_metrics(second, entry_id=None)

    assert is_new is False
    assert merged.id == entry.id  # same row, not a sibling
    assert merged.steps == 12000  # sent field updated
    assert merged.weight == 70    # unsent fields survive
    assert merged.sleep_duration_minutes == 450

    all_rows = metrics_service.daily_metrics_repo.get_all()
    assert len(all_rows) == 1

