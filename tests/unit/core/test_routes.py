from datetime import datetime
from unittest.mock import patch

import pytest

from app.core.database import db_session
from app.modules.tasks.models import Task


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200

@pytest.mark.parametrize("hour, expected_greeting, expected_time", [
    # tuple with 3 values (corresponds to 3 parameter names above)
    (6, "Good morning!", "06:00:00"),
    (15, "Good afternoon!", "15:00:00"),
    (21, "Good evening!", "21:00:00"),
])
def test_home_greeting_and_time(client, hour, expected_greeting, expected_time):
    # Translation: "For the duration of this block, any reference to datetime 
    # in app.core.routes will use this mock."
    with patch("app.core.routes.datetime") as mock_dt:
        # So datetime.now() inside routes.py will use our fake 'now'
        # "When this test runs, and any code calls datetime.now(), give them this fake time instead"
        # So if our real code has:
        # now = datetime.now()
        # It will now get:
        # datetime(2024, 1, 1, hour, 0)
        mock_dt.now.return_value = datetime(2024, 1, 1, hour, 0)
        # Patching replaces the whole datetime class inside our route — not just .now().
        # So real code like datetime(...) would break without help, since mocks can't build real objects. (datetime is no longer the real datetime, just a mock object)
        # side_effect tells it: "Fake .now(), but act like real datetime() for everything else."
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        res = client.get("/")
        html = res.data.decode()

        assert expected_greeting in html
        assert expected_time in html

@pytest.mark.parametrize("tasks_to_seed, expected_titles", [
    (
        [
            Task(title="Anchor Habit", type="habit", is_anchor=True), # Should work
            Task(title="Wrong Type", type="todo", is_anchor=True),    # Should not work - not of right type
            Task(title="Not Anchor", type="habit", is_anchor=False)   # Should not work - incorrect is_anchor bool val
        ],
        ["Anchor Habit"]
    ),
])
def test_anchor_habit_filtering(client, tasks_to_seed, expected_titles):
    # Feed test DB tasks to test on
    db_session.add_all(tasks_to_seed)
    db_session.commit()

    response = client.get("/")
    html = response.data.decode() # How does this work exactly?

    # Check expected anchor habits are rendered
    for title in expected_titles:
        assert title in html

    # Ensure excluded ones aren't shown
    # Translation: “Create a set of task titles from the seeded tasks, 
    # but only include the ones that are not in the list of expected titles.”
    excluded_titles = {t.title for t in tasks_to_seed if t.title not in expected_titles}
    for title in excluded_titles:
        assert title not in html