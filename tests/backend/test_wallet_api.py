import pytest

def test_get_my_wallet(client, student_auth_headers):
    """Test retrieving student's wallet balance and transactions."""
    res = client.get("/api/wallet/me", headers=student_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "balance" in data
    assert float(data["balance"]) >= 0.0
    assert "transactions" in data
    assert isinstance(data["transactions"], list)

def test_top_up_wallet(client, student_auth_headers):
    """Test simulated wallet top-up."""
    # Get initial balance
    initial = client.get("/api/wallet/me", headers=student_auth_headers).json()["balance"]
    
    # Top up 250
    res = client.post("/api/wallet/topup", json={"amount": 250.0, "payment_reference": "Test Top-up"}, headers=student_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert float(data["balance"]) == float(initial) + 250.0

def test_wallet_payment_order_deduction(client, student_auth_headers):
    """Test placing an order using Wallet as payment method deducts from balance."""
    # 1. Top up ample balance
    client.post("/api/wallet/topup", json={"amount": 500.0}, headers=student_auth_headers)
    bal_before = float(client.get("/api/wallet/me", headers=student_auth_headers).json()["balance"])

    # 2. Place order with Wallet
    order_payload = {
        "items": [{"food_item_id": 1, "quantity": 1, "special_instructions": "Wallet test"}],
        "payment_method": "Wallet",
        "notes": "Testing wallet deduction"
    }
    order_res = client.post("/api/orders/", json=order_payload, headers=student_auth_headers)
    assert order_res.status_code == 201
    order_data = order_res.json()
    assert order_data["payment_method"] == "Campus Wallet"

    # 3. Verify wallet balance deducted
    bal_after = float(client.get("/api/wallet/me", headers=student_auth_headers).json()["balance"])
    assert bal_after < bal_before

def test_get_wallet_transactions(client, student_auth_headers):
    """Test retrieving student's wallet transaction ledger directly."""
    res = client.get("/api/wallet/transactions", headers=student_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "transaction_type" in data[0]
        assert "amount" in data[0]
