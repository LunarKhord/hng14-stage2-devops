import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import fakeredis.aioredis
import main

@pytest.fixture
def client():
    fake_redis = fakeredis.aioredis.FakeRedis()
    with patch('main.r', fake_redis):
        yield TestClient(main.app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_job(client):
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data

def test_get_job_not_found(client):
    response = client.get("/jobs/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"

def test_get_job_status(client):
    client.app.dependency_overrides = {}
    import main
    main.r.hget = fakeredis.aioredis.FakeRedis().hget
    response = client.get("/jobs/1234")
    assert response.status_code == 200