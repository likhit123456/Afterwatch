"""Functional tests for the target app (the `verify` stage).

These check that the app WORKS, not that it is secure. They must keep passing
after the defender agent patches the vulns, which proves the fixes did not break
behaviour. Security is asserted separately by security/redteam.py.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:  # context manager fires lifespan -> init_db()
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_valid_login(client):
    r = client.post("/login", json={"username": "alice", "password": "alice-pw"})
    assert r.status_code == 200
    assert r.json()["username"] == "alice"


def test_invalid_login_is_rejected(client):
    r = client.post("/login", json={"username": "alice", "password": "wrong"})
    assert r.status_code == 401
