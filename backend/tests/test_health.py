from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "finance-engine-api",
        "app_name": "Finance Engine API",
        "environment": "development",
        "version": "0.1.0",
    }
