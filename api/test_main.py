import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import main

@pytest.fixture
def client():
    # Create a mock Redis that returns None for hget (so endpoint can return 404)
    mock_redis = AsyncMock()
    mock_redis.hget = AsyncMock(return_value=None)
    # The hash set and list push are fine as default AsyncMock (they'll still work)
    with patch('main.r', mock_redis):
        main.app.dependency_overrides = {}
        yield TestClient(main.app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    # Match the actual API – it returns "healthy", not "ok"
    assert response.json() == {"status": "healthy"}

def test_create_job(client):
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)
    assert len(data["job_id"]) > 0


def test_get_job_status_not_found(client):
    response = client.get("/jobs/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_get_job_status(client):
    # Override just this test's hget to return "completed"
    mock_value = b"completed"
    main.r.hget = AsyncMock(return_value=mock_value)
    response = client.get("/jobs/1234")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"