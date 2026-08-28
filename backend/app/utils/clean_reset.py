"""
Database Safe Clean Data Reset Utility
Resets operational and transactional records (orders, items, payments, tokens, wallet txns, ratings, logs)
while strictly preserving the relational schema, tables, foreign keys, categories, food menu catalog, and system counters.
"""

import sys
import os

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.database.session import SessionLocal
from backend.app.models.order import Order, OrderItem
from backend.app.models.token import Token
from backend.app.models.payment import Payment
from backend.app.models.wallet import Wallet, WalletTransaction
from backend.app.models.rating import FoodRating
from backend.app.models.waste import FoodWasteLog
from backend.app.models.ai_data import PredictionOverride, DemandPrediction, QueuePrediction, UserPreference, Recommendation
from backend.app.models.user import User, RefreshToken
from backend.app.models.cart import CartItem
from backend.app.models.rewards import UserReward
from backend.app.models.food import FoodItem, Category
from backend.app.models.counter import Counter
from backend.app.models.notification import Notification

def reset_operational_data():
    db = SessionLocal()
    try:
        print("[1/4] Deleting child transaction and log records in reverse foreign-key order...")
        db.query(CartItem).delete()
        db.query(Notification).delete()
        db.query(FoodRating).delete()
        db.query(OrderItem).delete()
        db.query(Token).delete()
        db.query(Payment).delete()
        db.query(WalletTransaction).delete()
        db.query(FoodWasteLog).delete()
        db.query(PredictionOverride).delete()
        db.query(DemandPrediction).delete()
        db.query(QueuePrediction).delete()
        db.query(Recommendation).delete()
        db.query(RefreshToken).delete()
        db.query(UserPreference).delete()

        print("[2/4] Deleting operational orders...")
        db.query(Order).delete()

        print("[3/4] Removing temporary test students and cleaning wallets...")
        test_users = db.query(User).filter(User.role_id == 3).all()
        for u in test_users:
            db.query(Wallet).filter(Wallet.user_id == u.id).delete()
            db.query(UserReward).filter(UserReward.user_id == u.id).delete()
            db.delete(u)

        # Reset core admin & staff wallets to 0
        for u in db.query(User).filter(User.role_id.in_([1, 2])).all():
            w = db.query(Wallet).filter(Wallet.user_id == u.id).first()
            if w:
                w.balance = 0.0
            r = db.query(UserReward).filter(UserReward.user_id == u.id).first()
            if r:
                r.total_points = 0

        db.commit()
        print("[4/4] Clean data reset completed successfully!")

        print("\n--- DATABASE VERIFICATION SUMMARY ---")
        print(f"Users (Core Staff & Admin): {db.query(User).count()}")
        print(f"Orders: {db.query(Order).count()}")
        print(f"Order Items: {db.query(OrderItem).count()}")
        print(f"Payments: {db.query(Payment).count()}")
        print(f"Tokens: {db.query(Token).count()}")
        print(f"Wallet Transactions: {db.query(WalletTransaction).count()}")
        print(f"Food Items (Catalog Preserved): {db.query(FoodItem).count()}")
        print(f"Categories (Preserved): {db.query(Category).count()}")
        print(f"Counters (Preserved): {db.query(Counter).count()}")

    except Exception as e:
        db.rollback()
        print(f"Error during clean reset: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_operational_data()
