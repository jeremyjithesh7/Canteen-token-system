import os
import re

def test_frontend_files_exist_and_link_integrity():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_dir = os.path.join(base_dir, "frontend")

    required_html_files = [
        "index.html", "login.html", "register.html", "dashboard.html",
        "menu.html", "orders.html", "token.html", "profile.html",
        "cart.html", "queue.html", "kiosk.html",
        "admin/index.html", "admin/menu.html", "admin/orders.html",
        "admin/inventory.html", "admin/analytics.html", "admin/users.html", "admin/notifications.html"
    ]

    for rel_path in required_html_files:
        full_path = os.path.join(frontend_dir, rel_path)
        assert os.path.exists(full_path), f"Missing frontend page: {rel_path}"

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify essential styles and API scripts are linked
        assert "css/style.css" in content, f"Missing style.css link in {rel_path}"
        assert "js/api.js" in content or "api.js" in content, f"Missing api.js in {rel_path}"
        
        # Verify no unfinished placeholders
        assert "TODO" not in content, f"Unfinished TODO placeholder found in {rel_path}"
