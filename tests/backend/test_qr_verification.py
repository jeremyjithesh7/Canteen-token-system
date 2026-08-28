import pytest

def test_qr_verification_valid_token(client, student_auth_headers, staff_auth_headers):
    """Test staff verifying student token and QR payload."""
    # 1. Top up wallet and place order to generate instant token
    client.post("/api/wallet/topup", json={"amount": 150.0, "payment_method": "UPI"}, headers=student_auth_headers)

    order_payload = {
        "items": [{"food_item_id": 1, "quantity": 1}],
        "payment_method": "Wallet"
    }
    order_res = client.post("/api/orders/", json=order_payload, headers=student_auth_headers)
    assert order_res.status_code == 201
    order_data = order_res.json()
    tok_num = order_data["token_number"]
    assert tok_num is not None

    # 2. Staff verifies token by number
    v_res = client.get(f"/api/tokens/verify-qr?token_str={tok_num}", headers=staff_auth_headers)
    assert v_res.status_code == 200
    v_data = v_res.json()
    assert v_data["token_number"] == tok_num
    assert v_data["is_already_collected"] is False
    assert len(v_data["items"]) > 0
    tok_id = v_data["token_id"]

    # 3. Staff marks token collected
    m_res = client.post(f"/api/tokens/{tok_id}/mark-collected", headers=staff_auth_headers)
    assert m_res.status_code == 200
    assert m_res.json()["status"] in ["Collected", "Completed"]

    # 4. Verify duplicate detection on re-check
    v_recheck = client.get(f"/api/tokens/verify-qr?token_str={tok_num}", headers=staff_auth_headers)
    assert v_recheck.status_code == 200
    assert v_recheck.json()["is_already_collected"] is True

def test_qr_verification_invalid_token(client, staff_auth_headers):
    """Test verification failure on non-existent token."""
    res = client.get("/api/tokens/verify-qr?token_str=INVALID-TOKEN-9999", headers=staff_auth_headers)
    assert res.status_code == 404
