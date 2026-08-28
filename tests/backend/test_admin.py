import pytest
from fastapi.testclient import TestClient

def test_admin_dashboard_metrics(client: TestClient, admin_auth_headers):
    response = client.get("/api/admin/dashboard-stats", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "today_revenue" in data
    assert "total_orders_today" in data
    assert "active_queue_count" in data
    assert "low_stock_count" in data
    assert "status_distribution" in data
    assert "top_selling_items" in data
    assert "revenue_trends" in data
    assert "peak_hours" in data
    assert isinstance(data["peak_hours"], list)
    assert len(data["peak_hours"]) > 0
    assert "hour" in data["peak_hours"][0]
    assert "orders" in data["peak_hours"][0]

def test_admin_user_management(client: TestClient, admin_auth_headers):
    # Ensure at least one student exists
    client.post("/api/auth/register", json={
        "name": "Admin Test Student",
        "email": "admintest.student@canteen.edu",
        "password": "Student@123",
        "phone": "+1-555-4321",
        "department": "Civil"
    })
    response = client.get("/api/users/", headers=admin_auth_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2
    student_user = next(u for u in users if u["role_id"] == 3)

    # Toggle status
    res_toggle = client.put(f"/api/users/{student_user['id']}/status?is_active=false", headers=admin_auth_headers)
    assert res_toggle.status_code == 200
    assert res_toggle.json()["is_active"] is False

    # Restore active status
    res_restore = client.put(f"/api/users/{student_user['id']}/status?is_active=true", headers=admin_auth_headers)
    assert res_restore.status_code == 200
    assert res_restore.json()["is_active"] is True

def test_broadcast_announcements(client: TestClient, admin_auth_headers):
    payload = {
        "title": "Evening Tea Special",
        "message": "Kulhad Chai & Samosa combo at 15% discount at Counter 3",
        "type": "promo"
    }
    response = client.post("/api/notifications/broadcast", json=payload, headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["recipients_count"] > 0
