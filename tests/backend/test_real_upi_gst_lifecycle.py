import pytest
from fastapi.testclient import TestClient

def test_single_item_40_rupees_gst_calculation(client: TestClient, student_auth_headers):
    """
    Test user requirement: Order a ₹40 item (e.g. Idli - 2 pcs)
    Subtotal = ₹40.00
    5% Campus GST = ₹2.00
    Final Total = ₹42.00
    """
    res = client.post("/api/orders/", json={
        "items": [{"food_item_id": 4, "quantity": 1}], # Idli = 40.00
        "payment_method": "UPI"
    }, headers=student_auth_headers)
    assert res.status_code == 201
    data = res.json()

    assert float(data["subtotal"]) == 40.00
    assert float(data["tax_amount"]) == 2.00
    assert float(data["final_amount"]) == 42.00
    assert data["status"] == "Payment_Pending"
    assert data["payment_status"] == "Pending"
    assert data["token_number"] is None

    # Check UPI URI structure
    uri = data["upi_payment_uri"]
    assert "jeremyjithesh7@oksbi" in uri or "jeremyjithesh7%40oksbi" in uri
    assert "am=42.00" in uri
    assert "cu=INR" in uri

def test_multiple_items_exact_gst_calculation(client: TestClient, student_auth_headers):
    """
    Test multiple items:
    - 2x Masala Dosa (65.00 x 2 = 130.00)
    - 1x Filter Coffee (25.00 x 1 = 25.00)
    - 3x Gulab Jamun (40.00 x 3 = 120.00)
    Subtotal = 130.00 + 25.00 + 120.00 = 275.00
    5% Campus GST = round(275.00 * 0.05, 2) = 13.75
    Final Total = 275.00 + 13.75 = 288.75
    """
    res = client.post("/api/orders/", json={
        "items": [
            {"food_item_id": 1, "quantity": 2}, # Masala Dosa
            {"food_item_id": 19, "quantity": 1}, # Filter Coffee
            {"food_item_id": 16, "quantity": 3}  # Gulab Jamun
        ],
        "payment_method": "UPI"
    }, headers=student_auth_headers)
    assert res.status_code == 201
    data = res.json()

    assert float(data["subtotal"]) == 275.00
    assert float(data["tax_amount"]) == 13.75
    assert float(data["final_amount"]) == 288.75
    assert "am=288.75" in data["upi_payment_uri"]

def test_utr_submission_and_staff_verification(client: TestClient, student_auth_headers, staff_auth_headers):
    """
    Test student submitting UTR reference:
    - Order remains Payment_Pending
    - Staff / Admin confirms payment -> Order becomes Confirmed, Token issued.
    """
    res = client.post("/api/orders/", json={
        "items": [{"food_item_id": 1, "quantity": 1}],
        "payment_method": "UPI"
    }, headers=student_auth_headers)
    order_id = res.json()["id"]

    # Student submits UTR
    utr_res = client.post(f"/api/orders/{order_id}/submit-payment-reference", json={"utr_reference": "987654321012"}, headers=student_auth_headers)
    assert utr_res.status_code == 200
    assert utr_res.json()["status"] == "Payment_Pending"

    # Staff confirms payment
    conf_res = client.post(f"/api/orders/{order_id}/confirm-payment", json={}, headers=staff_auth_headers)
    assert conf_res.status_code == 200
    conf_data = conf_res.json()
    assert conf_data["status"] == "Confirmed"
    assert conf_data["payment_status"] == "Completed"
    assert conf_data["token_number"] is not None

def test_insufficient_wallet_balance_rejected(client: TestClient):
    """
    Test placing order when wallet balance is insufficient:
    Should return 400 Bad Request with clear message.
    """
    # 1. Register a fresh student with zero wallet balance
    email = "zerowallet@canteen.edu"
    client.post("/api/auth/register", json={
        "email": email,
        "name": "Zero Wallet User",
        "password": "Password123!",
        "role_id": 3
    })
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Place order with Wallet without top-up
    res = client.post("/api/orders/", json={
        "items": [{"food_item_id": 1, "quantity": 1}],
        "payment_method": "Wallet"
    }, headers=headers)
    assert res.status_code == 400
    assert "Insufficient Campus Wallet balance" in res.json()["detail"]
