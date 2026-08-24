

# ---- Time Tracking ----
def test_create_time_entry_valid(authenticated_client):
    resp = authenticated_client.post("/api/time_tracking/time_entries", json={
        "entry_date": "2026-03-20",
        "category": "Work",
        "started_at": "09:00",
        "ended_at": "11:00",
    })
    assert resp.status_code == 201

def test_create_time_entry_invalid(authenticated_client):
    resp = authenticated_client.post("/api/time_tracking/time_entries", json={
        "category": "",
        "started_at": "09:00",
    })
    assert resp.status_code == 400

def test_patch_time_entry_valid(authenticated_client):
    create = authenticated_client.post("/api/time_tracking/time_entries", json={
        "entry_date": "2026-03-20",
        "category": "Work",
        "started_at": "09:00",
        "ended_at": "11:00",
    })
    entry_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/time_tracking/time_entries/{entry_id}", json={
        "category": "Deep Work"
    })
    assert resp.status_code == 200

def test_patch_time_entry_invalid(authenticated_client):
    create = authenticated_client.post("/api/time_tracking/time_entries", json={
        "entry_date": "2026-03-20",
        "category": "Work",
        "started_at": "09:00",
        "ended_at": "11:00",
    })
    entry_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/time_tracking/time_entries/{entry_id}", json={
        "started_at": "not-a-time"
    })
    assert resp.status_code == 400
