import pytest
from app.modules.time_tracking.service import create_time_tracking_service
from app.modules.time_tracking.schemas import TimeEntryCreate
from app.shared.exceptions import ServiceError
from app._infra.database import db_session
from datetime import datetime, time

def make_service(logged_in_user):
    return create_time_tracking_service(
        db_session(), logged_in_user['id'], 'America/Chicago'
    )


def test_create_time_entry(app, logged_in_user):
    svc = make_service(logged_in_user)
    entry = svc.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category='Work',
        started_at=time(9, 00),
        ended_at=time(11, 0),
    ))
    assert entry.duration_minutes == 120
    assert entry.category == 'Work'


def test_overlap_rejected(app, logged_in_user):
    svc = make_service(logged_in_user)
    svc.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category='Work',
        started_at=time(9, 00),
        ended_at=time(11, 0),
    ))
    db_session.flush()

    with pytest.raises(ServiceError, match="overlap"):
        svc.create_time_entry(TimeEntryCreate(
            entry_date=datetime(2026, 3, 20),
            category='Meeting',
            started_at=time(10, 0),
            ended_at=time(12, 0),
        ))


def test_adjacent_entries_allowed(app, logged_in_user):
    svc = make_service(logged_in_user)
    svc.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category='Work',
        started_at=time(9, 00),
        ended_at=time(11, 0),
    ))
    db_session.flush()

    # Touching at endpoint — should be allowed
    entry2 = svc.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category='Lunch',
        started_at=time(11, 0),
        ended_at=time(12, 0),
    ))
    assert entry2.category == 'Lunch'


def test_end_before_start_rejected(app, logged_in_user):
    svc = make_service(logged_in_user)
    entry = svc.create_time_entry(TimeEntryCreate(
        entry_date=datetime(2026, 3, 20),
        category='Graveyard shift',
        started_at=time(23, 0),
        ended_at=time(2, 0),
    ))
    assert entry.duration_minutes == 180
