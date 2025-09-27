import pytest
import time_machine
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


from app.shared.view_mixins import TimestampedViewMixin


# Sanity test for time-machine, remove later
@time_machine.travel(datetime(2025, 9, 29, 10, 0, 0, tzinfo=ZoneInfo("UTC")))
def test_time_machine_basic():
    now = datetime.now(tz=ZoneInfo("UTC"))
    assert now == datetime(2025, 9, 29, 10, 0, 0, tzinfo=ZoneInfo("UTC"))


# Since it's not @staticmethod, we need an instance.
# For testing, we don't care about the whole TimestampedViewMixin,
# we just need something with .due_date, ._tz, and .format()
class Dummy(TimestampedViewMixin):
    def __init__(self, due_date, tz="UTC"):
        self.due_date = due_date
        self._tz = tz


@pytest.mark.parametrize("days_offset, expected_label", [
    (-9, "Sep 20"), # Sat Sep 20, 2025
    (-1, "Yesterday"), # Sun Sep 28, 2025
    (0, "Today"), # Mon Sep 29, 2025
    (1, "Tomorrow"), # Tues Sep 30, 2025
    (2, "Wed"), # Wed Oct 1, 2025
    (6, "Sun"), # Sun Oct 5, 2025
    (7, "Oct 06"), # Mon Oct 6, 2025
])
@time_machine.travel(datetime(2025, 9, 29, 10, 0, 0, tzinfo=ZoneInfo("UTC")), tick=False)
def test_format_due_label(days_offset, expected_label):
    tz = "UTC"
    today = datetime(2025, 9, 29, 10, 0, tzinfo=ZoneInfo(tz))
    due_date = today + timedelta(days=days_offset)

    task = Dummy(due_date, tz)
    label = task.format_due_label(tz)

    assert label == expected_label