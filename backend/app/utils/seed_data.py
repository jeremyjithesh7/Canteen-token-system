"""
Database auto-seed utility for the Digital Canteen Token System.
Initializes tables and seeds initial roles, users, counters, categories, South Indian food items, inventory, ratings, and multi-week historical orders.
"""

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

from backend.app.models.user import Role, User
from backend.app.models.counter import Counter
from backend.app.models.food import Category, FoodItem, Menu, MenuItem
from backend.app.models.inventory import Inventory
from backend.app.models.order import Order, OrderItem
from backend.app.models.token import Token
from backend.app.models.payment import Payment
from backend.app.models.notification import Notification
from backend.app.models.ai_data import UserPreference, DemandPrediction, PredictionOverride, QueuePrediction
from backend.app.models.rating import FoodRating
from backend.app.models.cart import CartItem
from backend.app.models.wallet import Wallet, WalletTransaction
from backend.app.models.rewards import UserReward, UserAchievement
from backend.app.models.waste import FoodWasteLog
from backend.app.authentication.password import get_password_hash

def seed_database_if_empty(db: Session):
    """Checks if the database has seed data, and inserts it if empty."""
    # 1. Roles
    if db.query(Role).count() == 0:
        roles = [
            Role(id=1, name="admin", description="Canteen Manager with full administrative permissions"),
            Role(id=2, name="staff", description="Canteen kitchen and counter operator"),
            Role(id=3, name="student", description="College student ordering food and viewing tokens")
        ]
        db.add_all(roles)
        db.commit()

    # 2. Counters / Stalls
    if db.query(Counter).count() == 0:
        counters = [
            Counter(id=1, name="South Indian Tiffin & Meals", code="C1", station_type="Tiffin & Rice Meals", description="Dosas, Idlis, Vadas, Upma, Pongal, and Hot Rice Dishes", is_active=True, display_order=1),
            Counter(id=2, name="Desserts & Sweets Counter", code="C2", station_type="Traditional Sweets", description="Payasam, Mysore Pak, Kesari, Halwa, and Gulab Jamun", is_active=True, display_order=2),
            Counter(id=3, name="Beverages & Cafe Bar", code="C3", station_type="Coolers & Hot Brews", description="Filter Coffee, Masala Chai, Majjige, Coconut Water, and Soda", is_active=True, display_order=3)
        ]
        db.add_all(counters)
        db.commit()

    # 3. Users (Admin@123, Student@123, Staff@123)
    if db.query(User).count() == 0:
        default_pwd_hash = get_password_hash("Admin@123")
        student_pwd_hash = get_password_hash("Student@123")
        staff_pwd_hash = get_password_hash("Staff@123")

        users = [
            User(id=1, name="Canteen Administrator", email="admin@canteen.edu", phone="+1-555-0100", role_id=1, password_hash=default_pwd_hash, is_active=True, department="Canteen Management"),
            User(id=2, name="Aarav Sharma", email="student@canteen.edu", phone="+1-555-0101", role_id=3, password_hash=student_pwd_hash, is_active=True, department="Computer Science"),
            User(id=3, name="Priya Patel", email="priya@canteen.edu", phone="+1-555-0102", role_id=3, password_hash=student_pwd_hash, is_active=True, department="Electronics & Comm"),
            User(id=4, name="Rohan Mehta", email="rohan@canteen.edu", phone="+1-555-0103", role_id=3, password_hash=student_pwd_hash, is_active=True, department="Mechanical Eng"),
            User(id=5, name="Kitchen Counter Staff", email="staff@canteen.edu", phone="+1-555-0104", role_id=2, password_hash=staff_pwd_hash, is_active=True, department="Kitchen Operations")
        ]
        db.add_all(users)
        db.commit()

    # 4. Categories (3 Focused South Indian Categories)
    if db.query(Category).count() == 0:
        categories = [
            Category(id=1, name="South Indian Tiffin & Meals", slug="south-indian-tiffin-meals", description="Authentic crispy dosas, steamed idlis, fragrant rice bowls, and comforting tiffins.", display_order=1, icon="utensils", is_active=True),
            Category(id=2, name="Desserts", slug="desserts", description="Traditional South Indian sweets, rich ghee puddings, halwa, and melt-in-mouth delicacies.", display_order=2, icon="cookie", is_active=True),
            Category(id=3, name="Beverages", slug="beverages", description="Authentic filter coffee, soothing masala chai, fresh fruit juices, and cooling majjige.", display_order=3, icon="coffee", is_active=True)
        ]
        db.add_all(categories)
        db.commit()

    # 5. Food Items (25 Distinct Validated Photo Specialty URLs)
    if db.query(FoodItem).count() == 0:
        food_items_data = [
            # --- South Indian Tiffin & Meals (Category 1, Counter 1) ---
            (1, 1, 1, "Masala Dosa", "Crispy golden fermented crepe stuffed with aromatic spiced potato masala, served with hot sambar and fresh chutneys.", Decimal("65.00"), 8, True, True, True, "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80", 320, Decimal("7.5"), Decimal("52.0"), Decimal("9.0")),
            (2, 1, 1, "Plain Dosa", "Thin, crispy golden brown crepe served with piping hot vegetable lentil sambar and trio of coconut & tomato chutneys.", Decimal("50.00"), 6, True, True, True, "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=80", 260, Decimal("6.0"), Decimal("45.0"), Decimal("6.5")),
            (3, 1, 1, "Rava Dosa", "Lacy, crunchy roasted semolina crepe tempered with cumin, black pepper, ginger, and diced green chillies.", Decimal("70.00"), 10, True, True, True, "https://images.unsplash.com/photo-1516714435131-44d6b64dc6a2?w=600&auto=format&fit=crop&q=80", 310, Decimal("6.5"), Decimal("48.0"), Decimal("10.0")),
            (4, 1, 1, "Idli (2 pcs / plate)", "Fluffy, melt-in-the-mouth steamed rice and lentil cakes served with traditional drumstick sambar and fresh coconut chutney.", Decimal("40.00"), 4, True, True, True, "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&auto=format&fit=crop&q=80", 180, Decimal("7.0"), Decimal("36.0"), Decimal("2.0")),
            (5, 1, 1, "Medu Vada (2 pcs)", "Crispy golden fried savory lentil fritters with fluffy soft centers, infused with crushed peppercorns and curry leaves.", Decimal("45.00"), 5, True, True, True, "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80", 260, Decimal("8.0"), Decimal("28.0"), Decimal("13.0")),
            (6, 1, 1, "Uttapam (Onion Tomato)", "Thick, pillowy fermented pancake generously griddled with juicy chopped tomatoes, crunchy onions, and fresh cilantro.", Decimal("65.00"), 9, True, True, True, "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80", 330, Decimal("8.5"), Decimal("54.0"), Decimal("9.5")),
            (7, 1, 1, "Pongal (Ven Pongal)", "Comforting savory porridge of rice and yellow moong dal slow-cooked in pure ghee with cashews, crushed cumin, and ginger.", Decimal("55.00"), 5, True, False, True, "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop&q=80", 340, Decimal("9.0"), Decimal("48.0"), Decimal("14.0")),
            (8, 1, 1, "Upma (Rava Upma)", "Lightly roasted semolina cooked with mustard seeds, curry leaves, ginger, garden veggies, and crunchy roasted peanuts.", Decimal("40.00"), 4, True, True, True, "https://images.unsplash.com/photo-1610057099431-d73a1c9d2f2f?w=600&auto=format&fit=crop&q=80", 220, Decimal("5.5"), Decimal("38.0"), Decimal("5.0")),
            (9, 1, 1, "Sambar Rice", "Fragrant steamed rice slow-simmered in tangy tamarind, mixed country vegetables, and aromatic South Indian sambar spices.", Decimal("60.00"), 6, True, True, True, "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80", 380, Decimal("9.5"), Decimal("65.0"), Decimal("7.0")),
            (10, 1, 1, "Curd Rice", "Cooling creamy curd rice tempered with mustard seeds, fresh ginger, curry leaves, green chillies, and juicy pomegranate arils.", Decimal("50.00"), 3, True, False, True, "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop&q=80", 290, Decimal("7.0"), Decimal("44.0"), Decimal("8.5")),
            (11, 1, 1, "Bisi Bele Bath", "Classic Karnataka spicy hot lentil and rice dish loaded with vegetables, nutmeg, ghee, served with crunchy boondi.", Decimal("70.00"), 7, True, False, True, "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80", 410, Decimal("11.0"), Decimal("68.0"), Decimal("12.0")),
            (12, 1, 1, "Lemon Rice", "Zesty turmeric-infused basmati rice tossed with fresh lemon juice, crunchy peanuts, split lentils, and curry leaves.", Decimal("50.00"), 4, True, True, True, "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=600&auto=format&fit=crop&q=80", 310, Decimal("5.0"), Decimal("54.0"), Decimal("8.0")),

            # --- Desserts (Category 2, Counter 2) ---
            (13, 2, 2, "Payasam (Semiya/Vermicelli Kheer)", "Traditional sweet vermicelli pudding simmered in cardamom-infused whole milk, garnished with golden fried cashews and raisins.", Decimal("45.00"), 3, True, False, True, "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=600&auto=format&fit=crop&q=80", 280, Decimal("6.0"), Decimal("42.0"), Decimal("10.0")),
            (14, 2, 2, "Mysore Pak", "Royal heritage sweet crafted from roasted chickpea flour, pure desi ghee, and sugar that effortlessly melts in your mouth.", Decimal("40.00"), 2, True, False, True, "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80", 350, Decimal("4.0"), Decimal("45.0"), Decimal("18.0")),
            (15, 2, 2, "Rava Kesari", "Fragrant glowing golden semolina pudding enriched with pure ghee, saffron strands, cardamom, and roasted cashews.", Decimal("40.00"), 3, True, False, True, "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=600&auto=format&fit=crop&q=80", 310, Decimal("4.5"), Decimal("48.0"), Decimal("12.0")),
            (16, 2, 2, "Gulab Jamun (2 pcs)", "Soft golden milk dumplings soaked in warm rose and cardamom scented sugar syrup, served warm.", Decimal("40.00"), 2, True, False, True, "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&auto=format&fit=crop&q=80", 290, Decimal("4.0"), Decimal("50.0"), Decimal("9.0")),
            (17, 2, 2, "Badam Halwa", "Luxurious almond fudge prepared from blanched ground California almonds, Kashmiri saffron, and pure clarified butter.", Decimal("65.00"), 3, True, False, True, "https://images.unsplash.com/photo-1579372786545-d24232daf58c?w=600&auto=format&fit=crop&q=80", 380, Decimal("8.0"), Decimal("38.0"), Decimal("22.0")),
            (18, 2, 2, "Jalebi (100g)", "Crispy, crunchy golden pretzel spirals fried to perfection and drenched in fragrant saffron sugar syrup.", Decimal("40.00"), 3, True, True, True, "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=600&auto=format&fit=crop&q=80", 320, Decimal("2.5"), Decimal("62.0"), Decimal("8.0")),

            # --- Beverages (Category 3, Counter 3) ---
            (19, 3, 3, "Filter Coffee", "Iconic South Indian chicory blend freshly brewed in brass filters, frothed with hot creamy milk in traditional davarah & tumbler.", Decimal("25.00"), 3, True, False, True, "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=600&auto=format&fit=crop&q=80", 110, Decimal("3.5"), Decimal("15.0"), Decimal("4.0")),
            (20, 3, 3, "Masala Chai", "Aromatic full-bodied black tea brewed with crushed fresh ginger, green cardamom, cinnamon, and whole milk in an earthen kulhad.", Decimal("20.00"), 3, True, False, True, "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600&auto=format&fit=crop&q=80", 95, Decimal("2.8"), Decimal("14.0"), Decimal("3.2")),
            (21, 3, 3, "Buttermilk (Majjige/Chaas)", "Cooling spiced churned yogurt drink seasoned with roasted cumin, ginger, green chillies, curry leaves, and fresh coriander.", Decimal("25.00"), 2, True, False, True, "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=600&auto=format&fit=crop&q=80", 65, Decimal("3.0"), Decimal("6.0"), Decimal("2.2")),
            (22, 3, 3, "Tender Coconut Water", "100% pure naturally hydrating tender coconut water served chilled with freshly scooped soft coconut malai.", Decimal("45.00"), 2, True, True, True, "https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=600&auto=format&fit=crop&q=80", 45, Decimal("1.0"), Decimal("9.0"), Decimal("0.2")),
            (23, 3, 3, "Rose Milk", "Chilled milk flavored with fragrant Damascus rose extract, lightly sweetened and topped with soaked basil sabja seeds.", Decimal("35.00"), 2, True, False, True, "https://images.unsplash.com/photo-1556881286-fc6915169721?w=600&auto=format&fit=crop&q=80", 160, Decimal("4.0"), Decimal("24.0"), Decimal("5.0")),
            (24, 3, 3, "Sulaimani (Spiced Black Tea)", "Traditional Malabar spiced golden black tea infused with crushed cardamom, fresh mint, and a squeeze of fresh yellow lemon.", Decimal("20.00"), 3, True, True, True, "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80", 40, Decimal("0.5"), Decimal("9.0"), Decimal("0.0")),
            (25, 3, 3, "Fresh Lime Soda", "Fizzy chilled sparkling soda with freshly squeezed lime juice, rock salt, and mint (Sweet / Salt / Mixed).", Decimal("35.00"), 2, True, True, True, "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80", 80, Decimal("0.2"), Decimal("20.0"), Decimal("0.0"))
        ]

        food_items = []
        for fid, cid, cntr_id, name, desc, price, prep, veg, vegan, avail, img, cal, prot, carb, fat in food_items_data:
            food_items.append(FoodItem(
                id=fid, category_id=cid, counter_id=cntr_id, name=name, description=desc, price=price,
                prep_time_minutes=prep, is_veg=veg, is_vegan=vegan, is_available=avail,
                image_url=img, calories=cal, protein=prot, carbs=carb, fats=fat
            ))
        db.add_all(food_items)
        db.commit()

        # 6. Inventory for 25 Items
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

    # 7. Today's Menu (All 25 items active)
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

    # 8. Customer Ratings & Reviews
    if db.query(FoodRating).count() == 0:
        ratings = [
            FoodRating(user_id=2, food_item_id=1, rating=5, comment="Best Masala Dosa on campus! Super crispy and sambar is authentic."),
            FoodRating(user_id=3, food_item_id=19, rating=5, comment="Degree filter coffee is refreshing and piping hot."),
            FoodRating(user_id=4, food_item_id=4, rating=5, comment="Idlis are incredibly soft and melt in your mouth."),
            FoodRating(user_id=2, food_item_id=13, rating=5, comment="Payasam tastes just like homemade celebration kheer!"),
            FoodRating(user_id=3, food_item_id=21, rating=4, comment="Cooling Majjige with roasted jeera is perfect for hot afternoons.")
        ]
        db.add_all(ratings)
        db.commit()

    # 9. Rich Historical Orders, Tokens, Payments
    if db.query(Order).count() == 0:
        now = datetime.now()
        
        # Order 1: Completed (Counter 1)
        ord1 = Order(id=1, user_id=2, order_number="ORD-2026-1001", total_amount=Decimal("90.00"), discount_amount=Decimal("0.0"), final_amount=Decimal("90.00"), status="Completed", notes="Crispy dosa with extra sambar", created_at=now - timedelta(days=2))
        db.add(ord1)
        db.commit()
        db.add_all([
            OrderItem(order_id=1, food_item_id=1, quantity=1, unit_price=Decimal("65.00"), subtotal=Decimal("65.00")),
            OrderItem(order_id=1, food_item_id=19, quantity=1, unit_price=Decimal("25.00"), subtotal=Decimal("25.00")),
            Token(order_id=1, user_id=2, token_number="C1-101", status="Completed", estimated_wait_minutes=0, queue_position=0, counter_number=1, created_at=now - timedelta(days=2)),
            Payment(order_id=1, user_id=2, transaction_id="TXN-90238120", payment_method="UPI", amount=Decimal("90.00"), status="Completed", payment_date=now - timedelta(days=2))
        ])
        db.commit()

        # Order 2: Ready (Counter 1)
        ord2 = Order(id=2, user_id=4, order_number="ORD-2026-1002", total_amount=Decimal("85.00"), discount_amount=Decimal("0.0"), final_amount=Decimal("85.00"), status="Ready", notes="Medium sweet", created_at=now - timedelta(minutes=15))
        db.add(ord2)
        db.commit()
        db.add_all([
            OrderItem(order_id=2, food_item_id=4, quantity=1, unit_price=Decimal("40.00"), subtotal=Decimal("40.00")),
            OrderItem(order_id=2, food_item_id=13, quantity=1, unit_price=Decimal("45.00"), subtotal=Decimal("45.00")),
            Token(order_id=2, user_id=4, token_number="C1-102", status="Ready", estimated_wait_minutes=0, queue_position=1, counter_number=1, ready_at=now - timedelta(minutes=2), created_at=now - timedelta(minutes=15)),
            Payment(order_id=2, user_id=4, transaction_id="TXN-90238121", payment_method="Wallet", amount=Decimal("85.00"), status="Completed", payment_date=now - timedelta(minutes=15))
        ])
        db.commit()

        # Order 3: Preparing (Counter 1)
        ord3 = Order(id=3, user_id=3, order_number="ORD-2026-1003", total_amount=Decimal("70.00"), discount_amount=Decimal("0.0"), final_amount=Decimal("70.00"), status="Preparing", notes="Hot filter coffee", created_at=now - timedelta(minutes=6))
        db.add(ord3)
        db.commit()
        db.add_all([
            OrderItem(order_id=3, food_item_id=5, quantity=1, unit_price=Decimal("45.00"), subtotal=Decimal("45.00")),
            OrderItem(order_id=3, food_item_id=19, quantity=1, unit_price=Decimal("25.00"), subtotal=Decimal("25.00")),
            Token(order_id=3, user_id=3, token_number="C1-103", status="Preparing", estimated_wait_minutes=4, queue_position=1, counter_number=1, created_at=now - timedelta(minutes=6)),
            Payment(order_id=3, user_id=3, transaction_id="TXN-90238122", payment_method="Card", amount=Decimal("70.00"), status="Completed", payment_date=now - timedelta(minutes=6))
        ])
        db.commit()

        # Order 4: Ready at Counter 2 (Desserts)
        ord4 = Order(id=4, user_id=2, order_number="ORD-2026-1004", total_amount=Decimal("80.00"), discount_amount=Decimal("0.0"), final_amount=Decimal("80.00"), status="Ready", notes="Sweets packing", created_at=now - timedelta(minutes=10))
        db.add(ord4)
        db.commit()
        db.add_all([
            OrderItem(order_id=4, food_item_id=14, quantity=1, unit_price=Decimal("40.00"), subtotal=Decimal("40.00")),
            OrderItem(order_id=4, food_item_id=16, quantity=1, unit_price=Decimal("40.00"), subtotal=Decimal("40.00")),
            Token(order_id=4, user_id=2, token_number="C2-201", status="Ready", estimated_wait_minutes=0, queue_position=1, counter_number=2, ready_at=now - timedelta(minutes=1), created_at=now - timedelta(minutes=10)),
            Payment(order_id=4, user_id=2, transaction_id="TXN-90238123", payment_method="UPI", amount=Decimal("80.00"), status="Completed", payment_date=now - timedelta(minutes=10))
        ])
        db.commit()

        # Order 5: Ready at Counter 3 (Beverages)
        ord5 = Order(id=5, user_id=4, order_number="ORD-2026-1005", total_amount=Decimal("70.00"), discount_amount=Decimal("0.0"), final_amount=Decimal("70.00"), status="Ready", notes="Cold beverages", created_at=now - timedelta(minutes=8))
        db.add(ord5)
        db.commit()
        db.add_all([
            OrderItem(order_id=5, food_item_id=23, quantity=1, unit_price=Decimal("35.00"), subtotal=Decimal("35.00")),
            OrderItem(order_id=5, food_item_id=25, quantity=1, unit_price=Decimal("35.00"), subtotal=Decimal("35.00")),
            Token(order_id=5, user_id=4, token_number="C3-301", status="Ready", estimated_wait_minutes=0, queue_position=1, counter_number=3, ready_at=now - timedelta(minutes=3), created_at=now - timedelta(minutes=8)),
            Payment(order_id=5, user_id=4, transaction_id="TXN-90238124", payment_method="Wallet", amount=Decimal("70.00"), status="Completed", payment_date=now - timedelta(minutes=8))
        ])
        db.commit()

        # Generate 14-day multi-week realistic orders across all 25 items for demand prediction & analytics
        for day_offset in range(1, 15):
            day_time = now - timedelta(days=day_offset)
            num_orders = random.randint(20, 35)
            for j in range(num_orders):
                ord_id = 100 + (day_offset * 100) + j
                user_id = random.choice([2, 3, 4])
                item1_id = random.randint(1, 12) # Tiffin
                item2_id = random.choice([random.randint(13, 18), random.randint(19, 25)]) # Dessert or Beverage
                
                f1 = next((item for item in food_items_data if item[0] == item1_id), None)
                f2 = next((item for item in food_items_data if item[0] == item2_id), None)
                p1 = f1[5] if f1 else Decimal("50.00")
                p2 = f2[5] if f2 else Decimal("25.00")
                tot = p1 + p2

                ord_hist = Order(
                    id=ord_id,
                    user_id=user_id,
                    order_number=f"ORD-{day_time.strftime('%Y%m%d')}-{ord_id}",
                    total_amount=tot,
                    discount_amount=Decimal("0.0"),
                    final_amount=tot,
                    status="Completed",
                    created_at=day_time.replace(hour=random.randint(8, 20), minute=random.randint(0, 59))
                )
                db.add(ord_hist)
                db.commit()
                db.add_all([
                    OrderItem(order_id=ord_id, food_item_id=item1_id, quantity=1, unit_price=p1, subtotal=p1),
                    OrderItem(order_id=ord_id, food_item_id=item2_id, quantity=1, unit_price=p2, subtotal=p2),
                    Payment(order_id=ord_id, user_id=user_id, transaction_id=f"TXN-{day_offset}-{j}-{ord_id}-{random.randint(1000, 9999)}", payment_method=random.choice(["UPI", "Card", "Wallet"]), amount=tot, status="Completed", payment_date=ord_hist.created_at)
                ])
                db.commit()

    # 10. User Preferences
    if db.query(UserPreference).count() == 0:
        db.add_all([
            UserPreference(user_id=2, is_veg_only=True, spice_level="Medium", favorite_category_id=1, dietary_notes="High protein South Indian preference"),
            UserPreference(user_id=3, is_veg_only=True, spice_level="Mild", favorite_category_id=3, dietary_notes="Loves filter coffee and herbal teas")
        ])
        db.commit()

    # 11. Broadcast Notifications
    if db.query(Notification).count() == 0:
        db.add_all([
            Notification(user_id=2, title="Fresh South Indian Tiffins", message="Hot crispy Masala Dosas and steamed Idlis are now live at Counter 1!", type="announcement", is_read=False),
            Notification(user_id=3, title="Authentic Filter Coffee", message="Enjoy freshly brewed traditional Degree Filter Coffee at Counter 3.", type="promo", is_read=False)
        ])
        db.commit()

    # 12. Initial Demand Prediction Overrides
    if db.query(PredictionOverride).count() == 0:
        db.add_all([
            PredictionOverride(id=1, food_item_id=1, prediction_date=date.today(), meal_slot="Breakfast", original_predicted_quantity=45, override_quantity=60, reason="High morning student rush for Masala Dosa", admin_user_id=1),
            PredictionOverride(id=2, food_item_id=19, prediction_date=date.today(), meal_slot="Breakfast", original_predicted_quantity=70, override_quantity=90, reason="Morning exam rush filter coffee buffer", admin_user_id=1)
        ])
        db.commit()

    # 13. Campus Wallets
    if db.query(Wallet).count() == 0:
        for uid in [1, 2, 3, 4]:
            w = Wallet(user_id=uid, balance=Decimal("420.00") if uid in [2, 3] else Decimal("1000.00"))
            db.add(w)
            db.commit()
            db.add(WalletTransaction(
                wallet_id=w.id,
                user_id=uid,
                amount=w.balance,
                transaction_type="CREDIT",
                description="Campus Semester Welcome Credit"
            ))
            db.commit()

    # 14. User Rewards & Gamification
    if db.query(UserReward).count() == 0:
        db.add_all([
            UserReward(user_id=2, total_points=320, tier="Silver Foodie", current_streak_days=5, last_order_date=date.today() - timedelta(days=1)),
            UserReward(user_id=3, total_points=480, tier="Gold Gourmet", current_streak_days=12, last_order_date=date.today() - timedelta(days=1)),
            UserReward(user_id=4, total_points=160, tier="Bronze Explorer", current_streak_days=2, last_order_date=date.today() - timedelta(days=1))
        ])
        db.commit()

    # 15. User Achievements & Badges
    if db.query(UserAchievement).count() == 0:
        db.add_all([
            UserAchievement(user_id=2, achievement_key="FIRST_ORDER", title="First Order Placed", icon="🏆", description="Placed your first digital canteen order!"),
            UserAchievement(user_id=2, achievement_key="COFFEE_LOVER", title="Degree Coffee Fanatic", icon="☕", description="Ordered authentic Degree Filter Coffee 3+ times!"),
            UserAchievement(user_id=3, achievement_key="FIRST_ORDER", title="First Order Placed", icon="🏆", description="Placed your first digital canteen order!"),
            UserAchievement(user_id=3, achievement_key="STREAK_7", title="7-Day Canteen Streak", icon="🔥", description="Ordered food for 7 consecutive days!"),
            UserAchievement(user_id=3, achievement_key="FOODIE", title="Campus Foodie Pro", icon="🍛", description="Earned 250+ reward points exploring the menu!"),
            UserAchievement(user_id=4, achievement_key="FIRST_ORDER", title="First Order Placed", icon="🏆", description="Placed your first digital canteen order!")
        ])
        db.commit()

    # 16. Food Waste Logs (Historical 7-Day Audit)
    if db.query(FoodWasteLog).count() == 0:
        today = date.today()
        items = db.query(FoodItem).all()
        for day_offset in range(7, 0, -1):
            log_d = today - timedelta(days=day_offset)
            for item in items[:12]:
                prep = 45 + (item.id * 5 + day_offset * 3) % 35
                sold = int(prep * (0.84 + (item.id % 4) * 0.03))
                leftover = max(0, prep - sold)
                waste = int(leftover * 0.8)
                waste_pct = Decimal(str(round((waste / prep) * 100.0, 2)))
                cost = Decimal(str(round(waste * float(item.price) * 0.45, 2)))

                db.add(FoodWasteLog(
                    food_item_id=item.id,
                    log_date=log_d,
                    meal_slot="Lunch" if item.id % 2 == 0 else "Breakfast",
                    prepared_quantity=prep,
                    sold_quantity=sold,
                    leftover_quantity=leftover,
                    waste_quantity=waste,
                    waste_percentage=waste_pct,
                    waste_cost_inr=cost,
                    waste_reason="Over-preparation & unsold buffer"
                ))
        db.commit()
