from app.core.database import database_connection, db_session
from app.common.visualization.charts import get_time_entry_dataframe
from app.modules.time_tracking.models import TimeEntry
from datetime import datetime, timezone, timedelta
import pandas as pd

def test_get_time_entry_dataframe():

    with database_connection() as session:
        entry1 = TimeEntry(
            category="Programming",
            duration=30,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=30)
        )
        entry2 = TimeEntry(
            category="Programming",
            duration=30,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=30)
        )
        session.add(TimeEntry(category="Programming", duration=30, created_at=datetime.now(timezone.utc) - timedelta(days=2)))
        session.add(TimeEntry(category="Studying", duration=45))

        print(f"Session 1 ID: {id(session)}")

        print("HELLO THERE")

        # ACT
        session.flush()
        #print(f"Session 2 ID: {id(session)}")
        df = get_time_entry_dataframe(TimeEntry, "Programming", 7, session)
        print(f"got df:{df}")

        # DEBUG - see what's actually in there
        print(f"\n=== DEBUG ===")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame contents:\n{df}")
        print(f"Sum: {df['Programming'].sum() if 'Programming' in df.columns else 'No Programming column!'}")
        print(f"=============\n")

        # ASSERT
        assert len(df) == 2 # only 2 programming entries within given days
        assert df.columns.tolist() == ["Date", "Programming"]
        assert df["Programming"].sum() == 70 # duration 30 + 40
        print("HELLO THERE 2")

def test_also_get_time_entry_dataframe():
    
    print("TEST START")

    session = db_session()

    # Add one entry
    entry = TimeEntry(
        category="Programming",
        duration=30,
        created_at=datetime.now(timezone.utc)
    )

    session.add(entry)
    session.commit()
    print("Added entry")

    df = get_time_entry_dataframe(TimeEntry, "Programming", 7, session)
    print(f"Got df: {df}")

    print(f"Length: {len(df)}")
    assert len(df) == 1