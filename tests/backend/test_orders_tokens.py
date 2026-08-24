import pytest
from fastapi.testclient import TestClient

def test_place_order_and_generate_token_lifecycle(client: TestClient, student_auth_headers, admin_auth_headers):
    # 1. Place order
    order_payload = {
        "items": [
            {"food_item_id": 1, "quantity": 1, "special_instructions": "Crispy"},
            {"food_item_id": 14, "quantity": 2, "special_instructions": "Hot"}
        ],
        "payment_method": "UPI",
        "notes": "Table 4 pickup"
    }
    res_order = client.post("/api/orders/", json=order_payload, headers=student_auth_headers)
    assert res_order.status_code == 201
    order_data = res_order.json()

    assert "order_number" in order_data
    assert "token_number" in order_data
    token_num = order_data["token_number"]
    assert token_num.startswith("C1-") or token_num.startswith("C2-") or token_num.startswith("C3-")
    assert order_data["estimated_wait_minutes"] > 0
    assert order_data["counter_number"] in [1, 2, 3]

    order_id = order_data["id"]

    # 2. Check active token for user
    res_active = client.get("/api/tokens/active/me", headers=student_auth_headers)
    assert res_active.status_code == 200
    active_token = res_active.json()
    assert active_token["token_number"] == token_num
    token_id = active_token["id"]

    # 3. Admin advances token to 'Preparing'
    res_prep = client.put(f"/api/tokens/{token_id}/status", json={"status": "Preparing"}, headers=admin_auth_headers)
    assert res_prep.status_code == 200
    assert res_prep.json()["status"] == "Preparing"

    # 4. Admin advances token to 'Ready'
    res_ready = client.put(f"/api/tokens/{token_id}/status", json={"status": "Ready"}, headers=admin_auth_headers)
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "Ready"
    assert res_ready.json()["estimated_wait_minutes"] == 0

    # 5. Admin marks token 'Completed'
    res_comp = client.put(f"/api/tokens/{token_id}/status", json={"status": "Completed"}, headers=admin_auth_headers)
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "Completed"

def test_live_queue_board(client: TestClient):
    response = client.get("/api/tokens/live-board")
    assert response.status_code == 200
    tokens = response.json()
    assert isinstance(tokens, list)
