import pytest
from fastapi.testclient import TestClient

def test_place_order_and_generate_token_lifecycle(client: TestClient, student_auth_headers, admin_auth_headers):
    # 1. Place order via UPI
    order_payload = {
        "items": [
            {"food_item_id": 1, "quantity": 1, "special_instructions": "Crispy"}, # Masala Dosa 65.00
            {"food_item_id": 14, "quantity": 2, "special_instructions": "Fresh"} # Mysore Pak 40.00 x 2 = 80.00
        ],
        "payment_method": "UPI",
        "notes": "Table 4 pickup"
    }
    res_order = client.post("/api/orders/", json=order_payload, headers=student_auth_headers)
    assert res_order.status_code == 201
    order_data = res_order.json()

    # Verify Server-side Subtotal and 5% GST calculations
    # Subtotal = 65.00 + 80.00 = 145.00
    # 5% GST = 145.00 * 0.05 = 7.25
    # Total = 152.25
    assert float(order_data["subtotal"]) == 145.00
    assert float(order_data["tax_amount"]) == 7.25
    assert float(order_data["final_amount"]) == 152.25

    assert order_data["status"] == "Payment_Pending"
    assert order_data["payment_status"] == "Pending"
    assert order_data["upi_vpa"] == "jeremyjithesh7@oksbi"
    assert "upi://pay" in order_data["upi_payment_uri"]
    assert "jeremyjithesh7%40oksbi" in order_data["upi_payment_uri"] or "jeremyjithesh7@oksbi" in order_data["upi_payment_uri"]
    assert order_data["token_number"] is None # No token issued before payment verification

    order_id = order_data["id"]

    # 2. Student submits UTR reference
    res_utr = client.post(f"/api/orders/{order_id}/submit-payment-reference", json={"utr_reference": "423981729012"}, headers=student_auth_headers)
    assert res_utr.status_code == 200
    assert res_utr.json()["status"] == "Payment_Pending"

    # 3. Staff / Admin verifies and confirms payment
    res_conf = client.post(f"/api/orders/{order_id}/confirm-payment", json={}, headers=admin_auth_headers)
    assert res_conf.status_code == 200
    conf_data = res_conf.json()
    assert conf_data["status"] == "Confirmed"
    assert conf_data["payment_status"] == "Completed"
    assert conf_data["token_number"] is not None
    token_num = conf_data["token_number"]
    assert token_num.startswith("C1-") or token_num.startswith("C2-") or token_num.startswith("C3-")

    # 4. Check active token for user
    res_active = client.get("/api/tokens/active/me", headers=student_auth_headers)
    assert res_active.status_code == 200
    active_token = res_active.json()
    assert active_token["token_number"] == token_num
    token_id = active_token["id"]

    # 5. Admin advances token to 'Preparing'
    res_prep = client.put(f"/api/tokens/{token_id}/status", json={"status": "Preparing"}, headers=admin_auth_headers)
    assert res_prep.status_code == 200
    assert res_prep.json()["status"] == "Preparing"

    # 6. Admin advances token to 'Ready'
    res_ready = client.put(f"/api/tokens/{token_id}/status", json={"status": "Ready"}, headers=admin_auth_headers)
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "Ready"
    assert res_ready.json()["estimated_wait_minutes"] == 0

    # 7. Admin marks token 'Completed'
    res_comp = client.put(f"/api/tokens/{token_id}/status", json={"status": "Completed"}, headers=admin_auth_headers)
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "Completed"

def test_wallet_instant_confirmation(client: TestClient, student_auth_headers):
    # Top up wallet first
    client.post("/api/wallet/topup", json={"amount": 300.0, "payment_method": "UPI"}, headers=student_auth_headers)

    # Place order with Wallet
    res = client.post("/api/orders/", json={
        "items": [{"food_item_id": 4, "quantity": 1}], # Idli 40.00 -> GST 2.00 -> Total 42.00
        "payment_method": "Wallet"
    }, headers=student_auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "Confirmed"
    assert data["payment_status"] == "Completed"
    assert data["token_number"] is not None
    assert float(data["subtotal"]) == 40.00
    assert float(data["tax_amount"]) == 2.00
    assert float(data["final_amount"]) == 42.00

def test_live_queue_board(client: TestClient):
    response = client.get("/api/tokens/live-board")
    assert response.status_code == 200
    tokens = response.json()
    assert isinstance(tokens, list)
