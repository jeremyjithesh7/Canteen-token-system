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
        assert img.startswith("http://") or img.startswith("https://") or img.startswith("/assets/menu/"), f"Dish '{name}' has invalid image URL: {img}"
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
        if item["average_rating"] is not None:
            assert 1.0 <= item["average_rating"] <= 5.0
        assert item["rating_count"] >= 0

def test_all_local_menu_images_exist_and_serve_200(client: TestClient):
    """
    Validation Test: Verifies that every single dish's image asset is accessible
    via the web server with HTTP 200 OK and is a non-empty image.
    """
    response = client.get("/api/food/items?only_available=false")
    assert response.status_code == 200
    items = response.json()

    for item in items:
        img_path = item.get("image_url")
        if img_path and img_path.startswith("/"):
            res_img = client.get(img_path)
            assert res_img.status_code == 200, f"Failed to serve image for '{item['name']}' at {img_path}"
            assert len(res_img.content) > 1000, f"Image for '{item['name']}' is empty or corrupt"

def test_strict_slug_to_image_correspondence(client: TestClient):
    """
    Permanent Regression Test:
    Guarantees every dish ID has the exact required slug and /assets/menu/<slug>.jpg path.
    """
    EXPECTED_MAP = {
        "Masala Dosa": ("masala-dosa", "/assets/menu/masala-dosa.jpg"),
        "Plain Dosa": ("plain-dosa", "/assets/menu/plain-dosa.jpg"),
        "Rava Dosa": ("rava-dosa", "/assets/menu/rava-dosa.jpg"),
        "Idli (2 pcs / plate)": ("idli", "/assets/menu/idli.jpg"),
        "Medu Vada (2 pcs)": ("medu-vada", "/assets/menu/medu-vada.jpg"),
        "Uttapam (Onion Tomato)": ("uttapam", "/assets/menu/uttapam.jpg"),
        "Pongal (Ven Pongal)": ("pongal", "/assets/menu/pongal.jpg"),
        "Upma (Rava Upma)": ("upma", "/assets/menu/upma.jpg"),
        "Sambar Rice": ("sambar-rice", "/assets/menu/sambar-rice.jpg"),
        "Curd Rice": ("curd-rice", "/assets/menu/curd-rice.jpg"),
        "Bisi Bele Bath": ("bisi-bele-bath", "/assets/menu/bisi-bele-bath.jpg"),
        "Lemon Rice": ("lemon-rice", "/assets/menu/lemon-rice.jpg"),
        "Payasam (Semiya/Vermicelli Kheer)": ("payasam", "/assets/menu/payasam.jpg"),
        "Mysore Pak": ("mysore-pak", "/assets/menu/mysore-pak.jpg"),
        "Rava Kesari": ("rava-kesari", "/assets/menu/rava-kesari.jpg"),
        "Gulab Jamun (2 pcs)": ("gulab-jamun", "/assets/menu/gulab-jamun.jpg"),
        "Badam Halwa": ("badam-halwa", "/assets/menu/badam-halwa.jpg"),
        "Jalebi (100g)": ("jalebi", "/assets/menu/jalebi.jpg"),
        "Filter Coffee": ("filter-coffee", "/assets/menu/filter-coffee.jpg"),
        "Masala Chai": ("masala-chai", "/assets/menu/masala-chai.jpg"),
        "Buttermilk (Majjige/Chaas)": ("buttermilk", "/assets/menu/buttermilk.jpg"),
        "Tender Coconut Water": ("tender-coconut-water", "/assets/menu/tender-coconut-water.jpg"),
        "Rose Milk": ("rose-milk", "/assets/menu/rose-milk.jpg"),
        "Sulaimani (Spiced Black Tea)": ("sulaimani", "/assets/menu/sulaimani.jpg"),
        "Fresh Lime Soda": ("fresh-lime-soda", "/assets/menu/fresh-lime-soda.jpg")
    }

    response = client.get("/api/food/items?only_available=false")
    assert response.status_code == 200
    items = {item["name"]: item for item in response.json()}

    for name, (expected_slug, expected_img) in EXPECTED_MAP.items():
        assert name in items, f"Missing menu item: {name}"
        item = items[name]
        assert item.get("slug") == expected_slug, f"Slug mismatch for '{name}': got {item.get('slug')}, expected {expected_slug}"
        assert item.get("image_url") == expected_img, f"Image URL mismatch for '{name}': got {item.get('image_url')}, expected {expected_img}"
