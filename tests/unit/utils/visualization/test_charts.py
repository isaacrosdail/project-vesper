from app.core.database import database_connection
from app.utils.visualization.charts import get_dataframe
from app.modules.time_tracking.models import TimeEntry
import pandas as pd

def test_get_dataframe():

    # Arrange: Set up inputs & expected data
    model_name = TimeEntry
    category = ""
    days_ago = 7

    with database_connection() as session:

        df = get_dataframe(model_name, category, days_ago, session)

    # Assert
    assert not df.empty
    assert "Date" in df.columns