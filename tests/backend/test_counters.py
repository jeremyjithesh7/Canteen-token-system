import pytest
from fastapi.testclient import TestClient

def test_get_counters(client: TestClient):
    response = client.get("/api/counters/")
    assert response.status_code == 200
    counters = response.json()
    assert len(counters) >= 3
    codes = [c["code"] for c in counters]
    assert "C1" in codes
    assert "C2" in codes
    assert "C3" in codes

def test_admin_create_and_update_counter(client: TestClient, admin_auth_headers):
    # 1. Create counter
    new_counter = {
        "name": "Chef Express Wok",
        "code": "C4",
        "station_type": "Noodles & Stir-fries",
        "description": "Live wok kitchen for stir-fried noodles",
        "is_active": True,
        "display_order": 4
    }
    res_create = client.post("/api/counters/", json=new_counter, headers=admin_auth_headers)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["code"] == "C4"
    cid = created["id"]

    # 2. Update counter
    res_update = client.put(f"/api/counters/{cid}", json={"description": "Updated live wok kitchen"}, headers=admin_auth_headers)
    assert res_update.status_code == 200
    assert res_update.json()["description"] == "Updated live wok kitchen"
