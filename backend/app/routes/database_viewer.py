"""
Admin Database Inspector & Explorer API routes.
Provides real, read-only window into the live PostgreSQL/SQLite database tables
with pagination, search, sorting, filtering, and relational detail inspection.
All endpoints are strictly protected by JWT Admin-only RBAC (403 for non-admins).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

from backend.app.database.session import get_db
from backend.app.authentication.deps import get_current_admin
from backend.app.models.user import User, Role
from backend.app.models.order import Order, OrderItem
from backend.app.models.food import FoodItem, Category
from backend.app.models.counter import Counter
from backend.app.models.payment import Payment
from backend.app.models.wallet import Wallet, WalletTransaction
from backend.app.models.token import Token
from backend.app.models.waste import FoodWasteLog
from backend.app.models.rating import FoodRating
from backend.app.models.inventory import Inventory, InventoryLog
from backend.app.models.ai_data import PredictionOverride, DemandPrediction, QueuePrediction, UserPreference

router = APIRouter(prefix="/api/admin/database", tags=["Admin Database Viewer"])


@router.get("/overview")
def get_database_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Returns real live counts from all active tables in PostgreSQL.
    """
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role_id == 3).count()
    total_staff = db.query(User).filter(User.role_id == 2).count()
    total_admins = db.query(User).filter(User.role_id == 1).count()

    total_orders = db.query(Order).count()
    waiting_orders = db.query(Order).filter(Order.status == "Waiting").count()
    preparing_orders = db.query(Order).filter(Order.status == "Preparing").count()
    ready_orders = db.query(Order).filter(Order.status == "Ready").count()
    completed_orders = db.query(Order).filter(Order.status == "Completed").count()
    cancelled_orders = db.query(Order).filter(Order.status == "Cancelled").count()

    total_menu_items = db.query(FoodItem).count()
    available_menu_items = db.query(FoodItem).filter(FoodItem.is_available == True).count()

    total_payments = db.query(Payment).count()
    successful_payments = db.query(Payment).filter(Payment.status == "Completed").count()

    total_wallet_transactions = db.query(WalletTransaction).count()
    total_wallets = db.query(Wallet).count()

    total_tokens = db.query(Token).count()
    active_tokens = db.query(Token).filter(Token.status.in_(["Waiting", "Preparing", "Ready"])).count()

    total_counters = db.query(Counter).count()
    total_waste_logs = db.query(FoodWasteLog).count()
    total_ratings = db.query(FoodRating).count()
    total_inventory_logs = db.query(InventoryLog).count()
    total_overrides = db.query(PredictionOverride).count()

    return {
        "engine": db.bind.dialect.name.upper(),
        "counts": {
            "total_users": total_users,
            "total_students": total_students,
            "total_staff": total_staff,
            "total_admins": total_admins,
            "total_orders": total_orders,
            "waiting_orders": waiting_orders,
            "preparing_orders": preparing_orders,
            "ready_orders": ready_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_menu_items": total_menu_items,
            "available_menu_items": available_menu_items,
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "total_wallet_transactions": total_wallet_transactions,
            "total_wallets": total_wallets,
            "total_tokens": total_tokens,
            "active_tokens": active_tokens,
            "total_counters": total_counters,
            "total_waste_logs": total_waste_logs,
            "total_ratings": total_ratings,
            "total_inventory_logs": total_inventory_logs,
            "total_prediction_overrides": total_overrides
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/users")
def get_database_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: Optional[str] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'users' table. Passwords & hashes are excluded at query time.
    """
    query = db.query(User).join(Role, User.role_id == Role.id)

    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            User.name.ilike(s),
            User.email.ilike(s),
            User.phone.ilike(s),
            User.department.ilike(s)
        ))
    if role_id is not None:
        query = query.filter(User.role_id == role_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = query.order_by(User.id.asc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for u in users:
        items.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "role_id": u.role_id,
            "role_name": u.role.name if u.role else "Unknown",
            "department": u.department,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None
        })

    return {
        "table": "users",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/orders")
def get_database_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    counter_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'orders' table joined with user, token, and payment info.
    """
    query = db.query(Order).join(User, Order.user_id == User.id).outerjoin(Token, Order.id == Token.order_id)

    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            Order.order_number.ilike(s),
            User.name.ilike(s),
            User.email.ilike(s),
            Token.token_number.ilike(s)
        ))
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if counter_id:
        query = query.filter(Token.counter_number == counter_id)

    total = query.count()
    orders = query.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for o in orders:
        items.append({
            "id": o.id,
            "order_number": o.order_number,
            "user_id": o.user_id,
            "customer_name": o.user.name if o.user else "Unknown",
            "customer_email": o.user.email if o.user else "",
            "total_amount": float(o.total_amount),
            "discount_amount": float(o.discount_amount or 0),
            "final_amount": float(o.final_amount),
            "status": o.status,
            "token_number": o.token.token_number if o.token else None,
            "token_status": o.token.status if o.token else None,
            "counter_number": o.token.counter_number if o.token else 1,
            "payment_method": o.payment.payment_method if o.payment else "N/A",
            "payment_status": o.payment.status if o.payment else "N/A",
            "notes": o.notes,
            "items_count": len(o.items),
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "updated_at": o.updated_at.isoformat() if o.updated_at else None
        })

    return {
        "table": "orders",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/orders/{order_id}/details")
def get_database_order_relational_details(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Centrepiece inspection endpoint: Returns full relational graph for a single order:
    User -> Order -> OrderItems (with FoodItem details) -> Payment -> Token -> Matching Wallet Txn -> Rating
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order #{order_id} not found in database.")

    user = order.user
    token = order.token
    payment = order.payment

    # Order items with food details
    items = []
    for oi in order.items:
        food = oi.food_item
        items.append({
            "order_item_id": oi.id,
            "food_item_id": oi.food_item_id,
            "food_name": food.name if food else f"Food #{oi.food_item_id}",
            "category": food.category.name if (food and food.category) else "Meals",
            "quantity": oi.quantity,
            "unit_price": float(oi.unit_price),
            "subtotal": float(oi.subtotal),
            "special_instructions": oi.special_instructions,
            "prep_time_minutes": food.prep_time_minutes if food else 5,
            "calories": food.calories if food else None,
            "protein": float(food.protein) if (food and food.protein) else None
        })

    # Matching wallet transaction if paid via wallet
    wallet_txn = db.query(WalletTransaction).filter(WalletTransaction.reference_order_id == order.id).first()
    
    # Matching food ratings for this order
    ratings = db.query(FoodRating).filter(
        or_(FoodRating.order_id == order.id, FoodRating.user_id == order.user_id)
    ).all()

    return {
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "total_amount": float(order.total_amount),
            "discount_amount": float(order.discount_amount or 0),
            "final_amount": float(order.final_amount),
            "status": order.status,
            "notes": order.notes,
            "is_preorder": order.is_preorder,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        },
        "customer": {
            "id": user.id if user else None,
            "name": user.name if user else "Unknown",
            "email": user.email if user else "",
            "phone": user.phone if user else "",
            "department": user.department if user else "",
            "role": user.role.name if (user and user.role) else "student"
        },
        "order_items": items,
        "token": {
            "id": token.id if token else None,
            "token_number": token.token_number if token else None,
            "counter_number": token.counter_number if token else None,
            "status": token.status if token else None,
            "estimated_wait_minutes": token.estimated_wait_minutes if token else None,
            "queue_position": token.queue_position if token else None,
            "priority_score": float(token.priority_score) if (token and token.priority_score) else None,
            "called_at": token.called_at.isoformat() if (token and token.called_at) else None,
            "ready_at": token.ready_at.isoformat() if (token and token.ready_at) else None,
            "completed_at": token.completed_at.isoformat() if (token and token.completed_at) else None,
            "created_at": token.created_at.isoformat() if (token and token.created_at) else None
        } if token else None,
        "payment": {
            "id": payment.id if payment else None,
            "transaction_id": payment.transaction_id if payment else None,
            "payment_method": payment.payment_method if payment else None,
            "amount": float(payment.amount) if payment else None,
            "status": payment.status if payment else None,
            "payment_date": payment.payment_date.isoformat() if (payment and payment.payment_date) else None
        } if payment else None,
        "wallet_transaction": {
            "id": wallet_txn.id,
            "wallet_id": wallet_txn.wallet_id,
            "amount": float(wallet_txn.amount),
            "transaction_type": wallet_txn.transaction_type,
            "description": wallet_txn.description,
            "created_at": wallet_txn.created_at.isoformat() if wallet_txn.created_at else None
        } if wallet_txn else None,
        "ratings": [
            {
                "id": r.id,
                "food_item_id": r.food_item_id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in ratings
        ]
    }


@router.get("/order-items")
def get_database_order_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_id: Optional[int] = None,
    food_item_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'order_items' table.
    """
    query = db.query(OrderItem).join(Order, OrderItem.order_id == Order.id).join(FoodItem, OrderItem.food_item_id == FoodItem.id)

    if order_id:
        query = query.filter(OrderItem.order_id == order_id)
    if food_item_id:
        query = query.filter(OrderItem.food_item_id == food_item_id)

    total = query.count()
    items = query.order_by(OrderItem.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for oi in items:
        result.append({
            "id": oi.id,
            "order_id": oi.order_id,
            "order_number": oi.order.order_number if oi.order else f"ORD-{oi.order_id}",
            "food_item_id": oi.food_item_id,
            "food_name": oi.food_item.name if oi.food_item else f"Dish #{oi.food_item_id}",
            "category": oi.food_item.category.name if (oi.food_item and oi.food_item.category) else "Meals",
            "quantity": oi.quantity,
            "unit_price": float(oi.unit_price),
            "subtotal": float(oi.subtotal),
            "special_instructions": oi.special_instructions
        })

    return {
        "table": "order_items",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": result
    }


@router.get("/menu")
def get_database_menu(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    counter_id: Optional[int] = None,
    is_veg: Optional[bool] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'food_items' catalog table.
    """
    query = db.query(FoodItem).join(Category, FoodItem.category_id == Category.id)

    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            FoodItem.name.ilike(s),
            FoodItem.description.ilike(s)
        ))
    if category_id:
        query = query.filter(FoodItem.category_id == category_id)
    if counter_id:
        query = query.filter(FoodItem.counter_id == counter_id)
    if is_veg is not None:
        query = query.filter(FoodItem.is_veg == is_veg)
    if is_available is not None:
        query = query.filter(FoodItem.is_available == is_available)

    total = query.count()
    items = query.order_by(FoodItem.id.asc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for f in items:
        # Dynamic average rating from FoodRating table
        avg_rating = db.query(func.avg(FoodRating.rating)).filter(FoodRating.food_item_id == f.id).scalar()
        rating_count = db.query(FoodRating).filter(FoodRating.food_item_id == f.id).count()

        result.append({
            "id": f.id,
            "name": f.name,
            "category_id": f.category_id,
            "category_name": f.category.name if f.category else "Meals",
            "counter_id": f.counter_id,
            "price": float(f.price),
            "prep_time_minutes": f.prep_time_minutes,
            "is_veg": f.is_veg,
            "is_vegan": f.is_vegan,
            "is_available": f.is_available,
            "image_url": f.image_url,
            "calories": f.calories,
            "protein": float(f.protein) if f.protein else None,
            "carbs": float(f.carbs) if f.carbs else None,
            "fats": float(f.fats) if f.fats else None,
            "average_rating": round(float(avg_rating), 1) if avg_rating else None,
            "rating_count": rating_count,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })

    return {
        "table": "food_items",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": result
    }


@router.get("/payments")
def get_database_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: Optional[str] = None,
    payment_method: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'payments' table.
    """
    query = db.query(Payment).join(Order, Payment.order_id == Order.id).join(User, Payment.user_id == User.id)

    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            Payment.transaction_id.ilike(s),
            Order.order_number.ilike(s),
            User.name.ilike(s),
            User.email.ilike(s)
        ))
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)
    if status_filter:
        query = query.filter(Payment.status == status_filter)

    total = query.count()
    payments = query.order_by(Payment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for p in payments:
        items.append({
            "id": p.id,
            "order_id": p.order_id,
            "order_number": p.order.order_number if p.order else f"ORD-{p.order_id}",
            "user_id": p.user_id,
            "customer_name": p.order.user.name if (p.order and p.order.user) else "Unknown",
            "customer_email": p.order.user.email if (p.order and p.order.user) else "",
            "transaction_id": p.transaction_id,
            "payment_method": p.payment_method,
            "amount": float(p.amount),
            "status": p.status,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })

    return {
        "table": "payments",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/wallet-transactions")
def get_database_wallet_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: Optional[str] = None,
    txn_type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'wallet_transactions' table.
    """
    query = db.query(WalletTransaction).join(User, WalletTransaction.user_id == User.id)

    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            User.name.ilike(s),
            User.email.ilike(s),
            WalletTransaction.description.ilike(s)
        ))
    if txn_type:
        query = query.filter(WalletTransaction.transaction_type == txn_type)

    total = query.count()
    txns = query.order_by(WalletTransaction.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for t in txns:
        items.append({
            "id": t.id,
            "wallet_id": t.wallet_id,
            "user_id": t.user_id,
            "customer_name": t.user.name if t.user else "Unknown",
            "customer_email": t.user.email if t.user else "",
            "amount": float(t.amount),
            "transaction_type": t.transaction_type,
            "description": t.description,
            "reference_order_id": t.reference_order_id,
            "created_at": t.created_at.isoformat() if t.created_at else None
        })

    return {
        "table": "wallet_transactions",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/tokens")
def get_database_tokens(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    counter_number: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'tokens' table.
    """
    query = db.query(Token).join(Order, Token.order_id == Order.id).join(User, Token.user_id == User.id)

    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            Token.token_number.ilike(s),
            Order.order_number.ilike(s),
            User.name.ilike(s),
            User.email.ilike(s)
        ))
    if status_filter:
        query = query.filter(Token.status == status_filter)
    if counter_number:
        query = query.filter(Token.counter_number == counter_number)

    total = query.count()
    tokens = query.order_by(Token.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for t in tokens:
        items.append({
            "id": t.id,
            "token_number": t.token_number,
            "order_id": t.order_id,
            "order_number": t.order.order_number if t.order else f"ORD-{t.order_id}",
            "user_id": t.user_id,
            "customer_name": t.user.name if t.user else "Unknown",
            "counter_number": t.counter_number,
            "status": t.status,
            "estimated_wait_minutes": t.estimated_wait_minutes,
            "queue_position": t.queue_position,
            "priority_score": float(t.priority_score) if t.priority_score else 1.0,
            "called_at": t.called_at.isoformat() if t.called_at else None,
            "ready_at": t.ready_at.isoformat() if t.ready_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None
        })

    return {
        "table": "tokens",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/counters")
def get_database_counters(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'counters' configuration table.
    """
    counters = db.query(Counter).order_by(Counter.id.asc()).all()
    items = []
    for c in counters:
        active_count = db.query(Token).filter(
            Token.counter_number == c.id,
            Token.status.in_(["Waiting", "Preparing", "Ready"])
        ).count()

        items.append({
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "station_type": c.station_type,
            "description": c.description,
            "is_active": c.is_active,
            "display_order": c.display_order,
            "active_tokens_count": active_count
        })

    return {
        "table": "counters",
        "total": len(items),
        "items": items
    }


@router.get("/waste-logs")
def get_database_waste_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'food_waste_logs' table.
    """
    query = db.query(FoodWasteLog).join(FoodItem, FoodWasteLog.food_item_id == FoodItem.id)
    total = query.count()
    logs = query.order_by(FoodWasteLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for l in logs:
        items.append({
            "id": l.id,
            "food_item_id": l.food_item_id,
            "food_name": l.food_item.name if l.food_item else f"Dish #{l.food_item_id}",
            "log_date": l.log_date.isoformat() if l.log_date else None,
            "meal_slot": l.meal_slot,
            "prepared_quantity": l.prepared_quantity,
            "sold_quantity": l.sold_quantity,
            "leftover_quantity": l.leftover_quantity,
            "waste_quantity": l.waste_quantity,
            "waste_percentage": float(l.waste_percentage),
            "waste_cost_inr": float(l.waste_cost_inr),
            "waste_reason": l.waste_reason,
            "created_at": l.created_at.isoformat() if l.created_at else None
        })

    return {
        "table": "food_waste_logs",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/ratings")
def get_database_ratings(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries the live 'food_ratings' table.
    """
    query = db.query(FoodRating).join(User, FoodRating.user_id == User.id).join(FoodItem, FoodRating.food_item_id == FoodItem.id)
    total = query.count()
    ratings = query.order_by(FoodRating.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for r in ratings:
        items.append({
            "id": r.id,
            "food_item_id": r.food_item_id,
            "food_name": r.food_item.name if r.food_item else f"Dish #{r.food_item_id}",
            "user_id": r.user_id,
            "customer_name": r.user.name if r.user else "Student",
            "order_id": r.order_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    return {
        "table": "food_ratings",
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/ai-data")
def get_database_ai_data(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queries persisted AI override records and demand prediction tables from PostgreSQL.
    """
    overrides = db.query(PredictionOverride).join(FoodItem).all()
    override_items = []
    for o in overrides:
        override_items.append({
            "id": o.id,
            "food_item_id": o.food_item_id,
            "food_name": o.food_item.name if o.food_item else f"Dish #{o.food_item_id}",
            "prediction_date": o.prediction_date.isoformat() if o.prediction_date else None,
            "meal_slot": o.meal_slot,
            "original_predicted_quantity": o.original_predicted_quantity,
            "override_quantity": o.override_quantity,
            "reason": o.reason,
            "created_at": o.created_at.isoformat() if o.created_at else None
        })

    stored_predictions = db.query(DemandPrediction).limit(50).all()
    prediction_items = []
    for p in stored_predictions:
        prediction_items.append({
            "id": p.id,
            "food_item_id": p.food_item_id,
            "prediction_date": p.prediction_date.isoformat() if p.prediction_date else None,
            "meal_slot": p.meal_slot,
            "predicted_quantity": p.predicted_quantity,
            "actual_quantity": p.actual_quantity,
            "confidence_score": float(p.confidence_score) if p.confidence_score else 0.85
        })

    return {
        "table": "prediction_overrides & demand_predictions",
        "persisted_overrides": override_items,
        "stored_predictions": prediction_items,
        "ai_architecture_note": "AI Demand, Crowd Estimation, and Recommendation models operate via dynamic inference on genuine PostgreSQL order and inventory transaction logs."
    }
