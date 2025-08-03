from app.core.database import db_session
from app.common.visualization.charts import get_filtered_dataframe
from app.modules.time_tracking.models import TimeEntry
from datetime import datetime, timezone, timedelta

print("FILE IS BEING IMPORTED")

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
        print(f"Session 1 ID: {id(db_session)}")

        # ACT
        #print(f"Session 2 ID: {id(db_session)}")
        df = get_time_entry_dataframe(TimeEntry, "Programming", 7, db_session)
        print(f"got df:{df}")

        print("hey")
        # DEBUG - see what's actually in there
        print(f"\n=== DEBUG ===")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame contents:\n{df}")
        print(f"Sum: {df['Programming'].sum() if 'Programming' in df.columns else 'No Programming column!'}")
        print(f"=============\n")

        # ASSERT
        assert len(df) == 3 # only 2 programming entries within given days
        assert df.columns.tolist() == ["Date", "Programming"]
        assert df["Programming"].sum() == 90 # duration 30*3
        print("HELLO THERE 2")

def test_also_get_time_entry_dataframe(logged_in_user):
    print("TEST START")

    # ARRANGE
    entry = TimeEntry(
        category="Programming", 
        duration=30, 
        started_at=datetime.now(timezone.utc) - timedelta(days=1),
        user_id=logged_in_user.id
    )
    db_session.add(entry)
    db_session.commit()
    print("Added entry")

    df = get_time_entry_dataframe(TimeEntry, "Programming", 7, db_session)
    print(f"Got df: {df}")
    print(f"Length: {len(df)}")
    assert len(df) == 1