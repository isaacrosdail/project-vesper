

def test_missing_api_route_returns_json_error(authenticated_client):
    resp = authenticated_client.get("/api/nonexistent")
    response = resp.json

    assert response["code"] == "NOT_FOUND"
    assert resp.status_code == 404
    assert resp.content_type == "application/json"

def test_missing_template_route_returns_template(authenticated_client):
    resp = authenticated_client.get("/nonexistent")

    assert resp.status == "404 NOT FOUND"
    assert resp.content_type.startswith("text/html")
