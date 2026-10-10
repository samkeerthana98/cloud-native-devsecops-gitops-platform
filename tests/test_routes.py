"""Pytest tests for all Flask routes."""

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# --- GET / ---

def test_index_status(client):
    res = client.get("/")
    assert res.status_code == 200


def test_index_json_keys(client):
    res = client.get("/")
    data = res.get_json()
    assert data["name"] == "Cloud-Native DevSecOps & GitOps Delivery Platform"
    assert data["status"] == "running"


# --- GET /health ---

def test_health_status(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_health_json(client):
    res = client.get("/health")
    data = res.get_json()
    assert data["status"] == "healthy"


# --- GET /api/health ---

def test_api_health_status(client):
    res = client.get("/api/health")
    assert res.status_code == 200


def test_api_health_json(client):
    res = client.get("/api/health")
    data = res.get_json()
    assert data["status"] == "healthy"
