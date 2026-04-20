import pytest
from datetime import time, date
from app.shared.exceptions import ServiceError

def test_overlap_rejected(app, logged_in_user):
    from app.modules.time_tracking.service import create_time_tracking_service
    from app.modules.time_tracking.schemas import TimeEntryCreate
    from app._infra.database import db_session

    service = create_time_tracking_service(
        db_session(), logged_in_user['id'], 'America/Chicago'
    )

    # Create first entry
    service.create_time_entry(TimeEntryCreate(
        entry_date=date(2026, 3, 20),
        category='Work',
        started_at=time(9, 0),
        ended_at=time(11, 0),
    ))
    db_session.flush()

    # Overlapping entry should raise
    with pytest.raises(ServiceError, match="overlap"):
        service.create_time_entry(TimeEntryCreate(
            entry_date=date(2026, 3, 20),
            category='Meeting',
            started_at=time(10, 0),
            ended_at=time(12, 0),
        ))