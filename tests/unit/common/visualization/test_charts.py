from app.core.database import db_session
from app.common.visualization.charts import get_filtered_dataframe
from app.modules.time_tracking.models import TimeEntry
from datetime import datetime, timezone, timedelta

def test_get_filtered_dataframe(logged_in_user):
        # ARRANGE
        time_entries = [
            TimeEntry(
                category="Programming",
                duration=30,
                started_at=(datetime.now(timezone.utc) - timedelta(minutes=120)),
                user_id=logged_in_user.id
            ),
            # more entries
            TimeEntry(
                category="Programming",
                duration=30,
                started_at=datetime.now(timezone.utc) - timedelta(minutes=30),
                user_id=logged_in_user.id
            ),
            TimeEntry(
                category="Programming",
                duration=30, 
                started_at=datetime.now(timezone.utc) - timedelta(days=2),
                user_id=logged_in_user.id
            ),
        ]
        db_session.add_all(time_entries)
        db_session.flush()

        # ACT        
        df = get_filtered_dataframe(db_session, TimeEntry, logged_in_user.id, "category", "Programming", "duration", 7)

        # ASSERT
        assert len(df) == 3 # only 2 programming entries within given days
        assert df.columns.tolist() == ["Date", "Programming"]
        assert df["Programming"].sum() == 90 # duration 30*3

def test_also_get_filtered_dataframe(logged_in_user):
    # ARRANGE
    entry = TimeEntry(
        category="Programming", 
        duration=30, 
        started_at=datetime.now(timezone.utc) - timedelta(days=1),
        user_id=logged_in_user.id
    )
    db_session.add(entry)
    db_session.commit()
    
    # ACT
    df = get_filtered_dataframe(db_session, TimeEntry, logged_in_user.id, "category", "Programming", "duration", 7)

    # ASSERT
    assert len(df) == 1