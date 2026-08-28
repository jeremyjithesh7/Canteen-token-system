from .auth import router as auth_router
from .users import router as users_router
from .counters import router as counters_router
from .food import router as food_router
from .orders import router as orders_router
from .tokens import router as tokens_router
from .payments import router as payments_router
from .inventory import router as inventory_router
from .notifications import router as notifications_router
from .ai import router as ai_router
from .admin import router as admin_router
from .cart import router as cart_router
from .ratings import router as ratings_router
from .wallet import router as wallet_router
from .rewards import router as rewards_router
from .database_viewer import router as database_viewer_router

__all__ = [
    "auth_router",
    "users_router",
    "counters_router",
    "food_router",
    "orders_router",
    "tokens_router",
    "payments_router",
    "inventory_router",
    "notifications_router",
    "ai_router",
    "admin_router",
    "cart_router",
    "ratings_router",
    "wallet_router",
    "rewards_router",
    "database_viewer_router"
]
