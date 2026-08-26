from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_graceful_without_credentials():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert "connected" in payload
    assert payload["mode"] in ("cognodb", "demo", "fallback")


def test_search_returns_matching_project():
    response = client.get("/api/projects?q=climate")
    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "Climate Atlas"


def test_detail_contains_two_hop_connections():
    response = client.get("/api/projects/p1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["project"]["name"] == "Climate Atlas"
    assert any(item["id"] == "p2" for item in payload["connections"])


def test_missing_project_is_404():
    assert client.get("/api/projects/unknown").status_code == 404


def test_api_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data and "people" in data and "topics" in data and "relationships" in data
    assert data["projects"] >= 3


def test_home_page_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Pathfinder" in response.text
    assert "Climate Atlas" in response.text


def test_project_page_renders():
    response = client.get("/projects/p1")
    assert response.status_code == 200
    assert "Climate Atlas" in response.text
    assert "People in this orbit" in response.text


def test_project_page_404():
    response = client.get("/projects/unknown")
    assert response.status_code == 404
