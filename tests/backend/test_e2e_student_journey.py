import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.food import FoodItem
from backend.app.models.order import Order
from backend.app.models.rating import FoodRating
from backend.app.authentication.password import get_password_hash
from backend.app.authentication.jwt import create_access_token


def test_full_student_journey_and_honest_payment(client: TestClient, admin_auth_headers: dict):
    # 1. Register fresh student
    student_email = "test_journey_student@canteen.edu"
    student_pwd = "Password123!"
    client.post("/api/auth/register", json={
        "name": "Journey Student",
        "email": student_email,
        "password": student_pwd,
        "phone": "9123456780",
        "department": "Electrical Engineering",
        "role_id": 3
    })

    login_resp = client.post("/api/auth/login", json={"email": student_email, "password": student_pwd})
    student_token = login_resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    admin_headers = admin_auth_headers

    # 2. Get Menu - Verify 25 items & ratings initially empty
    resp = client.get("/api/food/items?only_available=false")
    assert resp.status_code == 200
    menu = resp.json()
    assert len(menu) == 25

    # Pick Plain Dosa (id=2) and Buttermilk (id=21)
    dosa = next(item for item in menu if item["slug"] == "plain-dosa")
    coffee = next(item for item in menu if item["slug"] == "buttermilk")

    dosa_price = Decimal(str(dosa["price"]))
    coffee_price = Decimal(str(coffee["price"]))

    # 3. Attempt rating before purchase (MUST FAIL with HTTP 403)
    rate_fail_resp = client.post(
        "/api/ratings/",
        json={"food_item_id": dosa["id"], "rating": 5, "comment": "Tried rating before ordering!"},
        headers=student_headers
    )
    assert rate_fail_resp.status_code == 403
    assert "order" in rate_fail_resp.json()["detail"].lower()

    # 4. Place Order via UPI checkout
    order_payload = {
        "items": [
            {"food_item_id": dosa["id"], "quantity": 2},
            {"food_item_id": coffee["id"], "quantity": 1}
        ],
        "payment_method": "UPI",
        "notes": "Crispy dosa please"
    }

    order_resp = client.post("/api/orders/", json=order_payload, headers=student_headers)
    assert order_resp.status_code == 201
    order_data = order_resp.json()

    order_id = order_data["id"]
    expected_subtotal = (dosa_price * 2) + (coffee_price * 1)
    expected_tax = (expected_subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
    expected_total = expected_subtotal + expected_tax

    assert Decimal(str(order_data["final_amount"])) == expected_total
    assert order_data["status"] == "Payment_Pending"
    assert order_data["upi_vpa"] == "jeremyjithesh7@oksbi"
    assert "upi://pay?" in order_data["upi_payment_uri"]

    # 5. Student submits UTR reference
    utr_resp = client.post(
        f"/api/orders/{order_id}/submit-payment-reference",
        json={"utr_reference": "UTR998877665544"},
        headers=student_headers
    )
    assert utr_resp.status_code == 200
    assert utr_resp.json()["status"] == "Payment_Pending"

    # 6. Staff verifies payment & token is issued
    confirm_resp = client.post(
        f"/api/orders/{order_id}/confirm-payment",
        headers=admin_headers
    )
    assert confirm_resp.status_code == 200
    confirmed_order = confirm_resp.json()
    assert confirmed_order["status"] == "Confirmed"
    assert confirmed_order["token_number"] is not None
    assert confirmed_order["token_status"] in ["Waiting", "Active", "Preparing", "Ready"]

    # 7. Move order through kitchen: Preparing -> Ready -> Completed
    status_resp = client.put(
        f"/api/orders/{order_id}/status",
        json={"status": "Completed"},
        headers=admin_headers
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "Completed"

    # 8. Now submit 5-star rating after genuine completion
    rate_resp = client.post(
        "/api/ratings/",
        json={
            "food_item_id": dosa["id"],
            "order_id": order_id,
            "rating": 5,
            "comment": "Authentic crispy Plain Dosa with great sambar!"
        },
        headers=student_headers
    )
    assert rate_resp.status_code == 201
    rate_data = rate_resp.json()
    assert rate_data["rating"] == 5
    assert rate_data["user_name"] == "Journey Student"

    # 9. Verify live average rating for Plain Dosa
    summary_resp = client.get(f"/api/ratings/dish/{dosa['id']}")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["average_rating"] == 5.0
    assert summary["rating_count"] == 1
    assert len(summary["latest_reviews"]) == 1
    assert summary["latest_reviews"][0]["comment"] == "Authentic crispy Plain Dosa with great sambar!"

    # 10. Verify Menu endpoint dynamically reflects updated average rating
    menu_updated = client.get("/api/food/items?only_available=false").json()
    updated_dosa = next(item for item in menu_updated if item["id"] == dosa["id"])
    assert updated_dosa["average_rating"] == 5.0
    assert updated_dosa["rating_count"] == 1
