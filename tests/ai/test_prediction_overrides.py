import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

def test_demand_override_creation_and_audit(client: TestClient, admin_auth_headers):
    target_date = (date.today() + timedelta(days=2)).isoformat()
    override_payload = {
        "food_item_id": 1,
        "prediction_date": target_date,
        "meal_slot": "Lunch",
        "override_quantity": 75,
        "reason": "College Alumni Meet Rush"
    }

    # 1. Post override
    res = client.post("/api/ai/demand-override", json=override_payload, headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["food_item_id"] == 1
    assert data["override_quantity"] == 75
    assert data["reason"] == "College Alumni Meet Rush"

    # 2. Get overrides list
    res_list = client.get("/api/ai/demand-overrides", headers=admin_auth_headers)
    assert res_list.status_code == 200
    overrides = res_list.json()
    assert len(overrides) >= 1
    assert any(o["override_quantity"] == 75 for o in overrides)

def test_demand_vs_actual_endpoint(client: TestClient, admin_auth_headers):
    res = client.get("/api/ai/demand-vs-actual?days=7", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "overall_accuracy" in data
    assert "data" in data
    assert len(data["data"]) > 0
    assert "predicted_demand" in data["data"][0]
    assert "actual_demand" in data["data"][0]
