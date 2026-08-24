import pytest
from ai.token_allocation.smart_allocator import SmartTokenAllocator

def test_smart_token_allocation():
    allocator = SmartTokenAllocator()

    order_items = [
        {"food_item_id": 1, "name": "Masala Dosa", "prep_time_minutes": 8, "category_slug": "breakfast", "quantity": 1},
        {"food_item_id": 14, "name": "Kulhad Chai", "prep_time_minutes": 3, "category_slug": "beverages", "quantity": 1}
    ]

    active_tokens = [
        {"id": 1, "status": "Preparing", "counter_number": 1},
        {"id": 2, "status": "Waiting", "counter_number": 2}
    ]

    decision = allocator.allocate_token(
        order_id=5,
        order_items=order_items,
        active_tokens=active_tokens
    )

    assert decision["token_number"] == "C1-105"
    assert decision["status"] == "Waiting"
    assert decision["counter_number"] == 1
    assert decision["estimated_wait_minutes"] >= 8
    assert decision["total_items_count"] == 2
