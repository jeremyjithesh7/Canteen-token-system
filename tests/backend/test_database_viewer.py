import pytest
from fastapi.testclient import TestClient

def test_database_viewer_forbidden_for_non_admin(client: TestClient, student_auth_headers):
    """Verify that non-admin student receives 403 Forbidden on database inspection endpoints."""
    res = client.get("/api/admin/database/overview", headers=student_auth_headers)
    assert res.status_code == 403

    res2 = client.get("/api/admin/database/users", headers=student_auth_headers)
    assert res2.status_code == 403

def test_database_viewer_unauthorized_without_token(client: TestClient):
    """Verify that unauthenticated requests receive 401 Unauthorized."""
    res = client.get("/api/admin/database/overview")
    assert res.status_code == 401

def test_database_overview_metrics(client: TestClient, admin_auth_headers):
    """Verify that admin can fetch genuine live database counts."""
    res = client.get("/api/admin/database/overview", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "counts" in data
    c = data["counts"]
    assert "total_users" in c
    assert "total_orders" in c
    assert "total_menu_items" in c
    assert "total_payments" in c
    assert "total_tokens" in c
    assert c["total_menu_items"] >= 25

def test_database_users_table_query(client: TestClient, admin_auth_headers):
    """Verify querying users table with password hashes stripped out."""
    res = client.get("/api/admin/database/users", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["table"] == "users"
    assert len(data["items"]) >= 2
    for u in data["items"]:
        assert "id" in u
        assert "email" in u
        assert "role_name" in u
        assert "password" not in u
        assert "password_hash" not in u

def test_database_menu_table_query_and_search(client: TestClient, admin_auth_headers):
    """Verify querying food menu catalog table with search filtering."""
    res = client.get("/api/admin/database/menu?search=Dosa", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["table"] == "food_items"
    assert len(data["items"]) >= 1
    assert any("Dosa" in item["name"] for item in data["items"])

def test_database_orders_and_relational_details(client: TestClient, student_auth_headers, admin_auth_headers):
    """Verify placing an order and inspecting its full relational graph."""
    # 1. Top up wallet
    client.post("/api/wallet/topup", json={"amount": 200.0, "payment_method": "UPI"}, headers=student_auth_headers)

    # 2. Place order
    order_res = client.post("/api/orders/", json={
        "items": [{"food_item_id": 1, "quantity": 1}],
        "payment_method": "Wallet",
        "notes": "Relational inspection test"
    }, headers=student_auth_headers)
    assert order_res.status_code == 201
    order_id = order_res.json()["id"]

    # 3. Query orders table from database viewer
    orders_table = client.get("/api/admin/database/orders", headers=admin_auth_headers)
    assert orders_table.status_code == 200
    assert any(o["id"] == order_id for o in orders_table.json()["items"])

    # 4. Query order-items table
    items_table = client.get(f"/api/admin/database/order-items?order_id={order_id}", headers=admin_auth_headers)
    assert items_table.status_code == 200
    assert len(items_table.json()["items"]) >= 1

    # 5. Deep relational traversal endpoint
    rel_res = client.get(f"/api/admin/database/orders/{order_id}/details", headers=admin_auth_headers)
    assert rel_res.status_code == 200
    rel_data = rel_res.json()
    assert rel_data["order"]["id"] == order_id
    assert rel_data["customer"]["email"] == "teststudent@canteen.edu"
    assert len(rel_data["order_items"]) == 1
    assert rel_data["order_items"][0]["food_name"] == "Masala Dosa"
    assert rel_data["payment"]["payment_method"] in ["Wallet", "Campus Wallet"]
    assert rel_data["token"]["counter_number"] == 1
    assert rel_data["wallet_transaction"] is not None
    assert rel_data["wallet_transaction"]["transaction_type"] == "DEBIT"

def test_database_tokens_and_payments_tables(client: TestClient, admin_auth_headers):
    """Verify querying payments and tokens tables."""
    pay_res = client.get("/api/admin/database/payments", headers=admin_auth_headers)
    assert pay_res.status_code == 200
    assert "items" in pay_res.json()

    tok_res = client.get("/api/admin/database/tokens", headers=admin_auth_headers)
    assert tok_res.status_code == 200
    assert "items" in tok_res.json()

def test_database_counters_and_ai_tables(client: TestClient, admin_auth_headers):
    """Verify querying counters and AI metadata."""
    c_res = client.get("/api/admin/database/counters", headers=admin_auth_headers)
    assert c_res.status_code == 200
    assert len(c_res.json()["items"]) >= 3

    ai_res = client.get("/api/admin/database/ai-data", headers=admin_auth_headers)
    assert ai_res.status_code == 200
    assert "ai_architecture_note" in ai_res.json()
