"""Transport-layer tests: routing, status codes, envelopes, persistence.

Validation *rules* live in test_habits_schemas.py — one invalid payload here
stands in for the whole class.
"""


def _create_payload(**overrides):
    return {
        "name": "Morning run",
        "type": "binary",
        "schedule_type": "weekly",
        "scheduled_days": [1, 3, 5],
        **overrides,
    }


def test_create_habit_valid(authenticated_client):
    resp = authenticated_client.post("/api/habits/habits", json=_create_payload())
    assert resp.status_code == 201
    data = resp.json["data"]
    assert data["schedule_type"] == "weekly"
    assert data["scheduled_days"] == [1, 3, 5]
    assert data["weekly_frequency"] is None


def test_create_habit_invalid_shape_returns_400(authenticated_client):
    # wrong param for the mode; the full matrix lives in the schema tests
    resp = authenticated_client.post("/api/habits/habits", json=_create_payload(
        scheduled_days=None, weekly_frequency=3,
    ))
    assert resp.status_code == 400


def test_patch_habit_rename(authenticated_client):
    create = authenticated_client.post("/api/habits/habits", json=_create_payload())
    habit_id = create.json["data"]["id"]

    resp = authenticated_client.patch(f"/api/habits/habits/{habit_id}", json={
        "name": "Evening run"
    })
    assert resp.status_code == 200
    assert resp.json["data"]["name"] == "Evening run"


def test_patch_schedule_mode_switch_replaces_group(authenticated_client):
    create = authenticated_client.post("/api/habits/habits", json=_create_payload())
    habit_id = create.json["data"]["id"]

    resp = authenticated_client.patch(f"/api/habits/habits/{habit_id}", json={
        "schedule_type": "frequency", "weekly_frequency": 3,
    })
    assert resp.status_code == 200
    data = resp.json["data"]
    assert data["schedule_type"] == "frequency"
    assert data["weekly_frequency"] == 3
    assert data["scheduled_days"] is None   # old mode's param cleared


def test_patch_habit_invalid_returns_400(authenticated_client):
    create = authenticated_client.post("/api/habits/habits", json=_create_payload())
    habit_id = create.json["data"]["id"]

    resp = authenticated_client.patch(f"/api/habits/habits/{habit_id}", json={
        "name": None
    })
    assert resp.status_code == 400
