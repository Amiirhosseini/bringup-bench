from fastapi.testclient import TestClient

from bringupbench.api import create_app
from bringupbench.config import AppConfig


def test_healthz():
    client = TestClient(create_app(AppConfig()))
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_snapshot_first_power():
    client = TestClient(create_app(AppConfig()))
    res = client.get("/v1/snapshot", params={"scenario": "first-power"})
    assert res.status_code == 200
    body = res.json()
    assert body["findings"]
    assert body["capture"]["events"]


def test_plan():
    client = TestClient(create_app(AppConfig()))
    res = client.post("/v1/plan", json={"goal": "diagnose i2c nack", "scenario": "first-power"})
    assert res.status_code == 200
    assert res.json()["steps"]
