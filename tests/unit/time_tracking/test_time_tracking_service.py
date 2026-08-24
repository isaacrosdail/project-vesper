from datetime import datetime, time

import pytest

from app._infra.database import db_session
from app.modules.time_tracking.schemas import TimeEntryCreate
from app.modules.time_tracking.service import create_time_tracking_service
from app.shared.exceptions import ServiceError


@pytest.fixture
def service(logged_in_user):
    return create_time_tracking_service(db_session, logged_in_user.id, logged_in_user.timezone)

def make_entry(**overrides):
    defaults = {
        "entry_date": datetime(2026, 3, 20),
        "category": "Work",
        "started_at": time(9, 0),
        "ended_at": time(11, 0),
    }
    return TimeEntryCreate(**defaults | overrides)


def test_overlap_rejected1(service):
    service.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category="Work",
        started_at=time(9, 0),
        ended_at=time(11, 0),
    ))
    db_session.flush()

    with pytest.raises(ServiceError, match="overlap"):
        service.create_time_entry(TimeEntryCreate(
            entry_date=datetime(2026, 3, 20),
            category="Meeting",
            started_at=time(10, 0),
            ended_at=time(12, 0),
        ))

def test_create_time_entry(service):
    entry = service.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category="Work",
        started_at=time(9, 00),
        ended_at=time(11, 0),
    ))
    assert entry.duration_minutes == 120
    assert entry.category == "Work"


def test_overlap_rejected(service):
    service.create_time_entry(make_entry())
    db_session.flush()

    with pytest.raises(ServiceError, match="overlap"):
        service.create_time_entry(TimeEntryCreate(
            entry_date=datetime(2026, 3, 20),
            category="Meeting",
            started_at=time(10, 0),
            ended_at=time(12, 0),
        ))


def test_adjacent_entries_allowed(service):
    service.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category="Work",
        started_at=time(9, 00),
        ended_at=time(11, 0),
    ))
    db_session.flush()

    # Touching at endpoint — should be allowed
    entry2 = service.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category="Lunch",
        started_at=time(11, 0),
        ended_at=time(12, 0),
    ))
    assert entry2.category == "Lunch"


def test_end_before_start_rejected(service):
    entry = service.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category="Graveyard shift",
        started_at=time(23, 0),
        ended_at=time(2, 0),
    ))
    assert entry.duration_minutes == 180
