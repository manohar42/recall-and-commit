from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check():
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "recall-and-commit-api"
    assert body["version"] == "0.1.0"