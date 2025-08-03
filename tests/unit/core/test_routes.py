from datetime import datetime
from unittest.mock import patch

import pytest



def test_home_route(authenticated_client):
    response = authenticated_client.get("/")
    assert response.status_code == 200

@pytest.mark.parametrize("hour, expected_greeting, expected_time", [
    # tuple with 3 values (corresponds to 3 parameter names above)
    (6, "Good morning", "06:00:00"),
    (15, "Good afternoon", "15:00:00"),
    (21, "Good evening", "21:00:00"),
])
def test_authenticated_home_greeting_and_time(authenticated_client, hour, expected_greeting, expected_time):
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
        # TODO: STUDY/DRILL
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        res = authenticated_client.get("/")
        html = res.data.decode()

        assert expected_greeting in html
        assert expected_time in html
