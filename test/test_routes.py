import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify /healthCheck returns 200 with standard envelope."""
    response = client.get("/healthCheck")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["code"] == 200
    assert data["data"]["checks"]["server"] == "ok"


def test_ready_check_endpoint():
    """Verify /ready probe returns standard envelope."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "dependencies" in data["data"]


def test_api_docs_html():
    """Verify /docs serves HTML Swagger documentation."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
