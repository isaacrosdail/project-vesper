
def test_create_daily_metrics(authenticated_client):
    response = authenticated_client.post("/api/metrics/daily_metrics", json={
        "entry_date": "2026-03-20",
        "steps": 8000,
        "calories": 2100,
    })
    assert response.status_code == 201


def test_create_metrics_valid(authenticated_client):
    resp = authenticated_client.post("/api/metrics/daily_metrics", json={
        "entry_date": "2026-03-20",
        "steps": 8000,
        "calories": 2100,
    })
    assert resp.status_code == 201

def test_create_metrics_invalid(authenticated_client):
    resp = authenticated_client.post("/api/metrics/daily_metrics", json={
        "steps": -500,
    })
    assert resp.status_code == 400

def test_patch_metrics_valid(authenticated_client):
    create = authenticated_client.post("/api/metrics/daily_metrics", json={
        "entry_date": "2026-03-20",
        "steps": 8000,
    })
    entry_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/metrics/daily_metrics/{entry_id}", json={
        "entry_date": "2026-03-20",
        "steps": 12000
    })
    assert resp.status_code == 200

def test_patch_metrics_invalid(authenticated_client):
    create = authenticated_client.post("/api/metrics/daily_metrics", json={
        "entry_date": "2026-03-20",
        "steps": 8000,
    })
    entry_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/metrics/daily_metrics/{entry_id}", json={
        "steps": -100
    })
    assert resp.status_code == 400

