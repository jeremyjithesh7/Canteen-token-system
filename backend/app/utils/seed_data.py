"""
Database master-data seed utility for the Digital Canteen Token System.
Seeds ONLY essential master/configuration catalog records:
- System Roles (admin, staff, student)
- Counters / Stalls (Counter 1, Counter 2, Counter 3)
- System Admin and Kitchen Staff accounts (for secure authentication)
- Categories (3 South Indian categories)
- Food Items (25 authentic South Indian dishes with pricing, prep time, nutritional info)
- Initial Inventory stock
- Today's Menu link

DOES NOT SEED fake students, fake orders, fake tokens, fake ratings,
fake wallet transactions, fake rewards, or fake food waste logs.
"""

from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal

from backend.app.models.user import Role, User
from backend.app.models.counter import Counter
from backend.app.models.food import Category, FoodItem, Menu, MenuItem
from backend.app.models.inventory import Inventory
from backend.app.authentication.password import get_password_hash

def seed_database_if_empty(db: Session):
    """Initializes master configuration and catalog data if the database is clean."""
    
    # 1. System Roles
    if db.query(Role).count() == 0:
        roles = [
            Role(id=1, name="admin", description="Canteen Manager with full administrative permissions"),
            Role(id=2, name="staff", description="Canteen kitchen and counter operator"),
            Role(id=3, name="student", description="College student ordering food and viewing tokens")
        ]
        db.add_all(roles)
        db.commit()

    # 2. Counters / Stalls (Master Configuration)
    if db.query(Counter).count() == 0:
        counters = [
            Counter(id=1, name="South Indian Tiffin & Meals", code="C1", station_type="Tiffin & Rice Meals", description="Dosas, Idlis, Vadas, Upma, Pongal, and Hot Rice Dishes", is_active=True, display_order=1),
            Counter(id=2, name="Desserts & Sweets Counter", code="C2", station_type="Traditional Sweets", description="Payasam, Mysore Pak, Kesari, Halwa, and Gulab Jamun", is_active=True, display_order=2),
            Counter(id=3, name="Beverages & Cafe Bar", code="C3", station_type="Coolers & Hot Brews", description="Filter Coffee, Masala Chai, Majjige, Coconut Water, and Soda", is_active=True, display_order=3)
        ]
        db.add_all(counters)
        db.commit()

    # 3. Base Operational Accounts (Admin & Staff for management and kitchen operations)
    if db.query(User).filter(User.role_id.in_([1, 2])).count() == 0:
        admin_pwd_hash = get_password_hash("Admin@123")
        staff_pwd_hash = get_password_hash("Staff@123")

        operational_users = [
            User(id=1, name="Canteen Administrator", email="admin@canteen.edu", phone="+1-555-0100", role_id=1, password_hash=admin_pwd_hash, is_active=True, department="Canteen Management"),
            User(id=2, name="Kitchen Counter Staff", email="staff@canteen.edu", phone="+1-555-0104", role_id=2, password_hash=staff_pwd_hash, is_active=True, department="Kitchen Operations")
        ]
        db.add_all(operational_users)
        db.commit()

    # 4. Food Categories (Master Data)
    if db.query(Category).count() == 0:
        categories = [
            Category(id=1, name="South Indian Tiffin & Meals", slug="south-indian-tiffin-meals", description="Authentic crispy dosas, steamed idlis, fragrant rice bowls, and comforting tiffins.", display_order=1, icon="utensils", is_active=True),
            Category(id=2, name="Desserts", slug="desserts", description="Traditional South Indian sweets, rich ghee puddings, halwa, and melt-in-mouth delicacies.", display_order=2, icon="cookie", is_active=True),
            Category(id=3, name="Beverages", slug="beverages", description="Authentic filter coffee, soothing masala chai, fresh fruit juices, and cooling majjige.", display_order=3, icon="coffee", is_active=True)
        ]
        db.add_all(categories)
        db.commit()

    # 5. Food Catalog Master Items (25 South Indian Specialties)
    if db.query(FoodItem).count() == 0:
        food_items_data = [
            # --- South Indian Tiffin & Meals (Category 1, Counter 1) ---
            (1, 1, 1, "Masala Dosa", "Crispy golden fermented crepe stuffed with aromatic spiced potato masala, served with hot sambar and fresh chutneys.", Decimal("65.00"), 8, True, True, True, "/assets/menu/masala-dosa.jpg", 320, Decimal("7.5"), Decimal("52.0"), Decimal("9.0")),
            (2, 1, 1, "Plain Dosa", "Thin, crispy golden brown crepe served with piping hot vegetable lentil sambar and trio of coconut & tomato chutneys.", Decimal("50.00"), 6, True, True, True, "/assets/menu/plain-dosa.jpg", 260, Decimal("6.0"), Decimal("45.0"), Decimal("6.5")),
            (3, 1, 1, "Rava Dosa", "Lacy, crunchy roasted semolina crepe tempered with cumin, black pepper, ginger, and diced green chillies.", Decimal("70.00"), 10, True, True, True, "/assets/menu/rava-dosa.jpg", 310, Decimal("6.5"), Decimal("48.0"), Decimal("10.0")),
            (4, 1, 1, "Idli (2 pcs / plate)", "Fluffy, melt-in-the-mouth steamed rice and lentil cakes served with traditional drumstick sambar and fresh coconut chutney.", Decimal("40.00"), 4, True, True, True, "/assets/menu/idli.jpg", 180, Decimal("7.0"), Decimal("36.0"), Decimal("2.0")),
            (5, 1, 1, "Medu Vada (2 pcs)", "Crispy golden fried savory lentil fritters with fluffy soft centers, infused with crushed peppercorns and curry leaves.", Decimal("45.00"), 5, True, True, True, "/assets/menu/medu-vada.jpg", 260, Decimal("8.0"), Decimal("28.0"), Decimal("13.0")),
            (6, 1, 1, "Uttapam (Onion Tomato)", "Thick, pillowy fermented pancake generously griddled with juicy chopped tomatoes, crunchy onions, and fresh cilantro.", Decimal("65.00"), 9, True, True, True, "/assets/menu/uttapam.jpg", 330, Decimal("8.5"), Decimal("54.0"), Decimal("9.5")),
            (7, 1, 1, "Pongal (Ven Pongal)", "Comforting savory porridge of rice and yellow moong dal slow-cooked in pure ghee with cashews, crushed cumin, and ginger.", Decimal("55.00"), 5, True, False, True, "/assets/menu/pongal.jpg", 340, Decimal("9.0"), Decimal("48.0"), Decimal("14.0")),
            (8, 1, 1, "Upma (Rava Upma)", "Lightly roasted semolina cooked with mustard seeds, curry leaves, ginger, garden veggies, and crunchy roasted peanuts.", Decimal("40.00"), 4, True, True, True, "/assets/menu/upma.jpg", 220, Decimal("5.5"), Decimal("38.0"), Decimal("5.0")),
            (9, 1, 1, "Sambar Rice", "Fragrant steamed rice slow-simmered in tangy tamarind, mixed country vegetables, and aromatic South Indian sambar spices.", Decimal("60.00"), 6, True, True, True, "/assets/menu/sambar-rice.jpg", 380, Decimal("9.5"), Decimal("65.0"), Decimal("7.0")),
            (10, 1, 1, "Curd Rice", "Cooling creamy curd rice tempered with mustard seeds, fresh ginger, curry leaves, green chillies, and juicy pomegranate arils.", Decimal("50.00"), 3, True, False, True, "/assets/menu/curd-rice.jpg", 290, Decimal("7.0"), Decimal("44.0"), Decimal("8.5")),
            (11, 1, 1, "Bisi Bele Bath", "Classic Karnataka spicy hot lentil and rice dish loaded with vegetables, nutmeg, ghee, served with crunchy boondi.", Decimal("70.00"), 7, True, False, True, "/assets/menu/bisi-bele-bath.jpg", 410, Decimal("11.0"), Decimal("68.0"), Decimal("12.0")),
            (12, 1, 1, "Lemon Rice", "Zesty turmeric-infused basmati rice tossed with fresh lemon juice, crunchy peanuts, split lentils, and curry leaves.", Decimal("50.00"), 4, True, True, True, "/assets/menu/lemon-rice.jpg", 310, Decimal("5.0"), Decimal("54.0"), Decimal("8.0")),

            # --- Desserts (Category 2, Counter 2) ---
            (13, 2, 2, "Payasam (Semiya/Vermicelli Kheer)", "Traditional sweet vermicelli pudding simmered in cardamom-infused whole milk, garnished with golden fried cashews and raisins.", Decimal("45.00"), 3, True, False, True, "/assets/menu/payasam.jpg", 280, Decimal("6.0"), Decimal("42.0"), Decimal("10.0")),
            (14, 2, 2, "Mysore Pak", "Royal heritage sweet crafted from roasted chickpea flour, pure desi ghee, and sugar that effortlessly melts in your mouth.", Decimal("40.00"), 2, True, False, True, "/assets/menu/mysore-pak.jpg", 350, Decimal("4.0"), Decimal("45.0"), Decimal("18.0")),
            (15, 2, 2, "Rava Kesari", "Fragrant glowing golden semolina pudding enriched with pure ghee, saffron strands, cardamom, and roasted cashews.", Decimal("40.00"), 3, True, False, True, "/assets/menu/rava-kesari.jpg", 310, Decimal("4.5"), Decimal("48.0"), Decimal("12.0")),
            (16, 2, 2, "Gulab Jamun (2 pcs)", "Soft golden milk dumplings soaked in warm rose and cardamom scented sugar syrup, served warm.", Decimal("40.00"), 2, True, False, True, "/assets/menu/gulab-jamun.jpg", 290, Decimal("4.0"), Decimal("50.0"), Decimal("9.0")),
            (17, 2, 2, "Badam Halwa", "Luxurious almond fudge prepared from blanched ground California almonds, Kashmiri saffron, and pure clarified butter.", Decimal("65.00"), 3, True, False, True, "/assets/menu/badam-halwa.jpg", 380, Decimal("8.0"), Decimal("38.0"), Decimal("22.0")),
            (18, 2, 2, "Jalebi (100g)", "Crispy, crunchy golden pretzel spirals fried to perfection and drenched in fragrant saffron sugar syrup.", Decimal("40.00"), 3, True, True, True, "/assets/menu/jalebi.jpg", 320, Decimal("2.5"), Decimal("62.0"), Decimal("8.0")),

            # --- Beverages (Category 3, Counter 3) ---
            (19, 3, 3, "Filter Coffee", "Iconic South Indian chicory blend freshly brewed in brass filters, frothed with hot creamy milk in traditional davarah & tumbler.", Decimal("25.00"), 3, True, False, True, "/assets/menu/filter-coffee.jpg", 110, Decimal("3.5"), Decimal("15.0"), Decimal("4.0")),
            (20, 3, 3, "Masala Chai", "Aromatic full-bodied black tea brewed with crushed fresh ginger, green cardamom, cinnamon, and whole milk in an earthen kulhad.", Decimal("20.00"), 3, True, False, True, "/assets/menu/masala-chai.jpg", 95, Decimal("2.8"), Decimal("14.0"), Decimal("3.2")),
            (21, 3, 3, "Buttermilk (Majjige/Chaas)", "Cooling spiced churned yogurt drink seasoned with roasted cumin, ginger, green chillies, curry leaves, and fresh coriander.", Decimal("25.00"), 2, True, False, True, "/assets/menu/buttermilk.jpg", 65, Decimal("3.0"), Decimal("6.0"), Decimal("2.2")),
            (22, 3, 3, "Tender Coconut Water", "100% pure naturally hydrating tender coconut water served chilled with freshly scooped soft coconut malai.", Decimal("45.00"), 2, True, True, True, "/assets/menu/tender-coconut-water.jpg", 45, Decimal("1.0"), Decimal("9.0"), Decimal("0.2")),
            (23, 3, 3, "Rose Milk", "Chilled milk flavored with fragrant Damascus rose extract, lightly sweetened and topped with soaked basil sabja seeds.", Decimal("35.00"), 2, True, False, True, "/assets/menu/rose-milk.jpg", 160, Decimal("4.0"), Decimal("24.0"), Decimal("5.0")),
            (24, 3, 3, "Sulaimani (Spiced Black Tea)", "Traditional Malabar spiced golden black tea infused with crushed cardamom, fresh mint, and a squeeze of fresh yellow lemon.", Decimal("20.00"), 3, True, True, True, "/assets/menu/sulaimani.jpg", 40, Decimal("0.5"), Decimal("9.0"), Decimal("0.0")),
            (25, 3, 3, "Fresh Lime Soda", "Fizzy chilled sparkling soda with freshly squeezed lime juice, rock salt, and mint (Sweet / Salt / Mixed).", Decimal("35.00"), 2, True, True, True, "/assets/menu/fresh-lime-soda.jpg", 80, Decimal("0.2"), Decimal("20.0"), Decimal("0.0"))
        ]

        food_items = []
        for fid, cid, cntr_id, name, desc, price, prep, veg, vegan, avail, img, cal, prot, carb, fat in food_items_data:
            slug = img.replace("/assets/menu/", "").replace(".jpg", "")
            food_items.append(FoodItem(
                id=fid, category_id=cid, counter_id=cntr_id, name=name, slug=slug, description=desc, price=price,
                prep_time_minutes=prep, is_veg=veg, is_vegan=vegan, is_available=avail,
                image_url=img, calories=cal, protein=prot, carbs=carb, fats=fat
            ))
        db.add_all(food_items)
        db.commit()

        # 6. Initial Stock Levels for Kitchen Operations
        inventory_items = []
        for item in food_items:
            stock_qty = 60 if item.category_id == 1 else (45 if item.category_id == 2 else 100)
            unit_name = "portions" if item.category_id == 1 else ("pieces" if item.category_id == 2 else "cups/glasses")
            inventory_items.append(Inventory(
                food_item_id=item.id,
                current_stock=stock_qty,
                minimum_stock_alert=12,
                unit=unit_name
            ))
        db.add_all(inventory_items)
        db.commit()

    # 7. Today's Menu Activation
    if db.query(Menu).count() == 0:
        today_menu = Menu(id=1, menu_date=date.today(), is_active=True)
        db.add(today_menu)
        db.commit()

        menu_items = [
            MenuItem(menu_id=1, food_item_id=fid, daily_stock_limit=120)
            for fid in range(1, 26)
        ]
        db.add_all(menu_items)
        db.commit()

    # 8. Synchronize PostgreSQL serial sequences to prevent primary key collision
    if db.bind and db.bind.dialect.name == "postgresql":
        from sqlalchemy import text
        table_sequence_map = [
            ("roles", "id"),
            ("counters", "id"),
            ("users", "id"),
            ("categories", "id"),
            ("food_items", "id"),
            ("menu", "id"),
            ("menu_items", "id"),
            ("inventory", "id")
        ]
        for tbl, pk_col in table_sequence_map:
            try:
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl}', '{pk_col}'), COALESCE(MAX({pk_col}), 1)) FROM {tbl};"))
                db.commit()
            except Exception:
                db.rollback()
