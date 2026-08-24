from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

from backend.app.models.order import Order, OrderItem
from backend.app.models.food import FoodItem
from backend.app.models.payment import Payment
from backend.app.models.cart import CartItem
from backend.app.schemas.order import OrderCreate, OrderStatusUpdate
from backend.app.utils.helpers import generate_order_number, generate_transaction_id
from backend.app.services.inventory_service import InventoryService
from backend.app.services.token_service import TokenService
from backend.app.services.wallet_service import WalletService
from backend.app.services.rewards_service import RewardsService

class OrderService:

    @staticmethod
    def create_order(db: Session, user_id: int, order_in: OrderCreate) -> Dict[str, Any]:
        """
        Processes full checkout flow:
        1. Validates food items & availability
        2. Deducts inventory stock
        3. Creates Order and OrderItem records
        4. Simulates instant payment confirmation / Campus Wallet deduction
        5. Issues smart token
        6. Accrues student reward points & updates streak
        """
        if not order_in.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain at least one item.")

        validated_items = []
        total_amount = Decimal("0.00")

        # 1. Validate items and compute totals
        for item_in in order_in.items:
            food_item = db.query(FoodItem).filter(FoodItem.id == item_in.food_item_id).first()
            if not food_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Food item {item_in.food_item_id} not found.")
            if not food_item.is_available:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Food item '{food_item.name}' is currently unavailable.")

            subtotal = food_item.price * item_in.quantity
            total_amount += subtotal

            validated_items.append({
                "food_item": food_item,
                "food_item_id": food_item.id,
                "quantity": item_in.quantity,
                "unit_price": food_item.price,
                "subtotal": subtotal,
                "special_instructions": item_in.special_instructions
            })

        # 2. Create Order Record & Deduct Inventory
        order_number = generate_order_number()
        for item in validated_items:
            InventoryService.deduct_stock_for_order(
                db=db,
                food_item_id=item["food_item_id"],
                quantity=item["quantity"],
                order_number=order_number
            )

        new_order = Order(
            user_id=user_id,
            order_number=order_number,
            total_amount=total_amount,
            discount_amount=Decimal("0.00"),
            final_amount=total_amount,
            status="Confirmed",
            notes=order_in.notes,
            scheduled_for=order_in.scheduled_for,
            is_preorder=order_in.is_preorder
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # 4. Create Order Items
        for item in validated_items:
            order_item = OrderItem(
                order_id=new_order.id,
                food_item_id=item["food_item_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
                special_instructions=item["special_instructions"]
            )
            db.add(order_item)
        db.commit()

        # 5. Handle Payment (Wallet deduction or UPI/Card/Cash)
        payment_method = order_in.payment_method or "UPI"
        if payment_method.lower() in ["wallet", "campus wallet"]:
            WalletService.deduct_wallet_for_order(db=db, user_id=user_id, order_id=new_order.id, amount=total_amount)
            payment_method = "Campus Wallet"

        txn_id = generate_transaction_id()
        payment = Payment(
            order_id=new_order.id,
            user_id=user_id,
            transaction_id=txn_id,
            payment_method=payment_method,
            amount=total_amount,
            status="Completed",
            gateway_response=f'{{"gateway": "DemoPay", "status": "SUCCESS", "txn_id": "{txn_id}"}}'
        )
        db.add(payment)
        db.commit()

        # 6. Clear server-side cart for user
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()

        # 7. Generate Smart Digital Token
        token = TokenService.generate_token_for_order(db=db, order=new_order)

        # 8. Accrue Gamification / Rewards points & calculate streak
        RewardsService.process_order_rewards(db=db, user_id=user_id, order_amount=total_amount)

        db.refresh(new_order)
        return {
            "order": new_order,
            "token": token,
            "payment": payment
        }

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def get_user_orders(db: Session, user_id: int) -> List[Order]:
        return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_all_orders(db: Session, status_filter: Optional[str] = None) -> List[Order]:
        query = db.query(Order).order_by(Order.created_at.desc())
        if status_filter:
            query = query.filter(Order.status == status_filter)
        return query.all()

    @staticmethod
    def update_order_status(db: Session, order_id: int, status_in: OrderStatusUpdate) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
        order.status = status_in.status
        order.updated_at = datetime.now()
        db.commit()
        db.refresh(order)
        return order
