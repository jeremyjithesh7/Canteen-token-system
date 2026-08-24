import pytest
from fastapi.testclient import TestClient

def test_all_food_items_have_unique_valid_images(client: TestClient):
    """
    Validation Test: Ensures every food item in the catalog has an authentic,
    non-empty, unique image URL with zero duplicate images across dishes.
    """
    response = client.get("/api/food/items?only_available=false")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 25, f"Expected at least 25 dishes, got {len(items)}"

    image_urls = []
    for item in items:
        img = item.get("image_url")
        name = item.get("name")
        assert img is not None and len(img.strip()) > 0, f"Dish '{name}' has missing image_url!"
        assert img.startswith("http://") or img.startswith("https://"), f"Dish '{name}' has invalid image URL: {img}"
        image_urls.append(img.strip())

    # Verify zero duplicate image URLs across all catalog items
    duplicates = [url for url in image_urls if image_urls.count(url) > 1]
    assert len(duplicates) == 0, f"Duplicate image URLs detected across unrelated dishes: {set(duplicates)}"

def test_food_items_contain_average_rating(client: TestClient):
    """
    Verifies that all food items return real star ratings and review counts.
    """
    response = client.get("/api/food/items")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert "average_rating" in item
        assert "rating_count" in item
        assert 1.0 <= item["average_rating"] <= 5.0
        assert item["rating_count"] >= 0
