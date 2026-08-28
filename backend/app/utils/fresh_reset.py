"""
Fresh Operational Reset script for CanteenOS.
Safely cleans out all test orders, payments, tokens, notifications,
demo student accounts, wallet histories, and fake ratings/reviews
while strictly preserving the 25-dish South Indian catalog and master config.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
from decimal import Decimal

from backend.app.database.session import SessionLocal, engine
from backend.app.database.base import Base
from backend.app.models import (
    Role, User, RefreshToken,
    Counter,
    Category, FoodItem, Menu, MenuItem,
    Inventory, InventoryLog,
    Order, OrderItem,
    Payment,
    Token,
    CartItem,
    Notification,
    UserPreference,
    Recommendation,
    DemandPrediction,
    PredictionOverride,
    QueuePrediction,
    FoodRating,
    Wallet, WalletTransaction,
    UserReward, UserAchievement,
    FoodWasteLog
)
from backend.app.authentication.password import get_password_hash

SLUG_MAP = {
    1: ("Masala Dosa", "masala-dosa", "/assets/menu/masala-dosa.jpg"),
    2: ("Plain Dosa", "plain-dosa", "/assets/menu/plain-dosa.jpg"),
    3: ("Rava Dosa", "rava-dosa", "/assets/menu/rava-dosa.jpg"),
    4: ("Idli (2 pcs / plate)", "idli", "/assets/menu/idli.jpg"),
    5: ("Medu Vada (2 pcs)", "medu-vada", "/assets/menu/medu-vada.jpg"),
    6: ("Uttapam (Onion Tomato)", "uttapam", "/assets/menu/uttapam.jpg"),
    7: ("Pongal (Ven Pongal)", "pongal", "/assets/menu/pongal.jpg"),
    8: ("Upma (Rava Upma)", "upma", "/assets/menu/upma.jpg"),
    9: ("Sambar Rice", "sambar-rice", "/assets/menu/sambar-rice.jpg"),
    10: ("Curd Rice", "curd-rice", "/assets/menu/curd-rice.jpg"),
    11: ("Bisi Bele Bath", "bisi-bele-bath", "/assets/menu/bisi-bele-bath.jpg"),
    12: ("Lemon Rice", "lemon-rice", "/assets/menu/lemon-rice.jpg"),
    13: ("Payasam (Semiya/Vermicelli Kheer)", "payasam", "/assets/menu/payasam.jpg"),
    14: ("Mysore Pak", "mysore-pak", "/assets/menu/mysore-pak.jpg"),
    15: ("Rava Kesari", "rava-kesari", "/assets/menu/rava-kesari.jpg"),
    16: ("Gulab Jamun (2 pcs)", "gulab-jamun", "/assets/menu/gulab-jamun.jpg"),
    17: ("Badam Halwa", "badam-halwa", "/assets/menu/badam-halwa.jpg"),
    18: ("Jalebi (100g)", "jalebi", "/assets/menu/jalebi.jpg"),
    19: ("Filter Coffee", "filter-coffee", "/assets/menu/filter-coffee.jpg"),
    20: ("Masala Chai", "masala-chai", "/assets/menu/masala-chai.jpg"),
    21: ("Buttermilk (Majjige/Chaas)", "buttermilk", "/assets/menu/buttermilk.jpg"),
    22: ("Tender Coconut Water", "tender-coconut-water", "/assets/menu/tender-coconut-water.jpg"),
    23: ("Rose Milk", "rose-milk", "/assets/menu/rose-milk.jpg"),
    24: ("Sulaimani (Spiced Black Tea)", "sulaimani", "/assets/menu/sulaimani.jpg"),
    25: ("Fresh Lime Soda", "fresh-lime-soda", "/assets/menu/fresh-lime-soda.jpg")
}

def perform_fresh_reset(db: Session = None):
    """Executes safe relational clean-up and establishes fresh operational state."""
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        # Ensure schema tables and columns exist
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE food_items ADD COLUMN IF NOT EXISTS slug VARCHAR(100);"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_food_items_slug ON food_items (slug);"))
            conn.commit()

        # 1. Delete transient operational/test child records in foreign-key order
        db.query(FoodRating).delete()
        db.query(WalletTransaction).delete()
        db.query(UserAchievement).delete()
        db.query(UserReward).delete()
        db.query(Notification).delete()
        db.query(CartItem).delete()
        db.query(Token).delete()
        db.query(Payment).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(FoodWasteLog).delete()
        db.query(PredictionOverride).delete()
        db.query(DemandPrediction).delete()
        db.query(QueuePrediction).delete()
        db.query(Recommendation).delete()
        db.query(InventoryLog).delete()
        db.query(RefreshToken).delete()
        db.query(UserPreference).delete()
        db.query(Wallet).delete()

        # 2. Delete test student users (retain role_id == 1 admin, role_id == 2 staff)
        db.query(User).filter(User.role_id == 3).delete()

        # 3. Ensure master roles exist
        if db.query(Role).count() == 0:
            roles = [
                Role(id=1, name="admin", description="Canteen Manager with full administrative permissions"),
                Role(id=2, name="staff", description="Canteen kitchen and counter operator"),
                Role(id=3, name="student", description="College student ordering food and viewing tokens")
            ]
            db.add_all(roles)
            db.commit()

        # 4. Ensure master counters exist
        if db.query(Counter).count() == 0:
            counters = [
                Counter(id=1, name="South Indian Tiffin & Meals", code="C1", station_type="Tiffin & Rice Meals", description="Dosas, Idlis, Vadas, Upma, Pongal, and Hot Rice Dishes", is_active=True, display_order=1),
                Counter(id=2, name="Desserts & Sweets Counter", code="C2", station_type="Traditional Sweets", description="Payasam, Mysore Pak, Kesari, Halwa, and Gulab Jamun", is_active=True, display_order=2),
                Counter(id=3, name="Beverages & Cafe Bar", code="C3", station_type="Coolers & Hot Brews", description="Filter Coffee, Masala Chai, Majjige, Coconut Water, and Soda", is_active=True, display_order=3)
            ]
            db.add_all(counters)
            db.commit()

        # 5. Ensure master categories exist
        if db.query(Category).count() == 0:
            categories = [
                Category(id=1, name="South Indian Tiffin & Meals", slug="south-indian-tiffin-meals", description="Authentic crispy dosas, steamed idlis, fragrant rice bowls, and comforting tiffins.", display_order=1, icon="utensils", is_active=True),
                Category(id=2, name="Desserts", slug="desserts", description="Traditional South Indian sweets, rich ghee puddings, halwa, and melt-in-mouth delicacies.", display_order=2, icon="cookie", is_active=True),
                Category(id=3, name="Beverages", slug="beverages", description="Authentic filter coffee, soothing masala chai, fresh fruit juices, and cooling majjige.", display_order=3, icon="coffee", is_active=True)
            ]
            db.add_all(categories)
            db.commit()

        # 6. Ensure admin & staff exist with fresh passwords
        admin = db.query(User).filter(User.email == "admin@canteen.edu").first()
        admin_pwd_hash = get_password_hash("Admin@123")
        if not admin:
            admin = User(id=1, name="Canteen Administrator", email="admin@canteen.edu", phone="+1-555-0100", role_id=1, password_hash=admin_pwd_hash, is_active=True, department="Canteen Management")
            db.add(admin)
        else:
            admin.password_hash = admin_pwd_hash

        staff = db.query(User).filter(User.email == "staff@canteen.edu").first()
        staff_pwd_hash = get_password_hash("Staff@123")
        if not staff:
            staff = User(id=2, name="Kitchen Counter Staff", email="staff@canteen.edu", phone="+1-555-0104", role_id=2, password_hash=staff_pwd_hash, is_active=True, department="Kitchen Operations")
            db.add(staff)
        else:
            staff.password_hash = staff_pwd_hash

        db.commit()

        # 7. Update/Seed all 25 Food Items with explicit slug and verified local asset
        for fid, (name, slug, img_path) in SLUG_MAP.items():
            food = db.query(FoodItem).filter(FoodItem.id == fid).first()
            if food:
                food.slug = slug
                food.image_url = img_path
                food.is_available = True
            else:
                # Re-create if missing
                cid = 1 if fid <= 12 else (2 if fid <= 18 else 3)
                cntr = cid
                price = Decimal("65.00") if fid == 1 else (Decimal("40.00") if fid == 4 else Decimal("50.00"))
                food = FoodItem(
                    id=fid, category_id=cid, counter_id=cntr, name=name, slug=slug,
                    price=price, prep_time_minutes=8, is_veg=True, is_available=True,
                    image_url=img_path, calories=250, protein=Decimal("6.0"),
                    carbs=Decimal("40.0"), fats=Decimal("6.0")
                )
                db.add(food)
        db.commit()

        # 8. Reset Inventory stock to clean level
        for fid in range(1, 26):
            inv = db.query(Inventory).filter(Inventory.food_item_id == fid).first()
            stock_qty = 60 if fid <= 12 else (45 if fid <= 18 else 100)
            if inv:
                inv.current_stock = stock_qty
            else:
                db.add(Inventory(food_item_id=fid, current_stock=stock_qty, minimum_stock_alert=10, unit="portions"))
        db.commit()

        # 9. Ensure today's active menu links all 25 items
        today = date.today()
        menu = db.query(Menu).first()
        if not menu:
            menu = Menu(menu_date=today, is_active=True)
            db.add(menu)
            db.commit()
            db.refresh(menu)
        else:
            menu.menu_date = today
            menu.is_active = True
            db.commit()

        db.query(MenuItem).filter(MenuItem.menu_id == menu.id).delete()
        for fid in range(1, 26):
            db.add(MenuItem(menu_id=menu.id, food_item_id=fid, daily_stock_limit=120))
        db.commit()

        print("✅ Fresh operational database reset executed successfully.")

    finally:
        if own_session:
            db.close()

if __name__ == "__main__":
    perform_fresh_reset()
