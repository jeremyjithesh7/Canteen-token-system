from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from backend.app.models.token import Token
from backend.app.models.order import Order, OrderItem
from backend.app.models.food import FoodItem
from backend.app.models.notification import Notification
from backend.app.schemas.token import TokenStatusUpdate
from ai.token_allocation.smart_allocator import SmartTokenAllocator

smart_allocator = SmartTokenAllocator()

class TokenService:

    @staticmethod
    def generate_token_for_order(db: Session, order: Order) -> Token:
        """
        Calculates optimal token sequencing using the Smart Token Allocator AI module,
        persists the token, and notifies the user.
        """
        # Fetch order items with prep times and categories
        order_items_data = []
        for oi in order.items:
            food = db.query(FoodItem).filter(FoodItem.id == oi.food_item_id).first()
            if food:
                order_items_data.append({
                    "food_item_id": food.id,
                    "name": food.name,
                    "prep_time_minutes": food.prep_time_minutes,
                    "category_slug": food.category.slug if food.category else "meals",
                    "quantity": oi.quantity
                })

        # Fetch currently active tokens in queue
        active_db_tokens = db.query(Token).filter(Token.status.in_(["Waiting", "Preparing"])).all()
        active_tokens_list = [
            {"id": t.id, "status": t.status, "counter_number": t.counter_number}
            for t in active_db_tokens
        ]

        # Execute Smart Token Allocation
        decision = smart_allocator.allocate_token(
            order_id=order.id,
            order_items=order_items_data,
            active_tokens=active_tokens_list
        )

        token = Token(
            order_id=order.id,
            user_id=order.user_id,
            token_number=decision["token_number"],
            status="Waiting",
            estimated_wait_minutes=decision["estimated_wait_minutes"],
            queue_position=decision["queue_position"],
            priority_score=Decimal(str(decision["priority_score"])),
            counter_number=decision["counter_number"]
        )
        db.add(token)
        db.commit()
        db.refresh(token)

        # Notify user
        notif = Notification(
            user_id=order.user_id,
            title=f"Token Assigned: {token.token_number}",
            message=f"Order {order.order_number} confirmed! Your Token is {token.token_number}. Estimated wait: ~{token.estimated_wait_minutes} mins at Counter {token.counter_number}.",
            type="token",
            reference_id=token.token_number
        )
        db.add(notif)
        db.commit()

        return token

    @staticmethod
    def get_token_by_id(db: Session, token_id: int) -> Optional[Token]:
        return db.query(Token).filter(Token.id == token_id).first()

    @staticmethod
    def get_token_by_order_id(db: Session, order_id: int) -> Optional[Token]:
        return db.query(Token).filter(Token.order_id == order_id).first()

    @staticmethod
    def get_user_tokens(db: Session, user_id: int) -> List[Token]:
        return db.query(Token).filter(Token.user_id == user_id).order_by(Token.created_at.desc()).all()

    @staticmethod
    def get_live_queue(db: Session) -> List[Dict[str, Any]]:
        """Returns all currently waiting and preparing tokens for the kitchen display & live board."""
        tokens = db.query(Token).filter(Token.status.in_(["Waiting", "Preparing", "Ready"])).order_by(Token.created_at.asc()).all()
        result = []
        for t in tokens:
            order = t.order
            user_name = order.user.name if order and order.user else "Customer"
            items_summary = ", ".join([f"{item.quantity}x {item.food_item.name}" for item in order.items if item.food_item]) if order else ""
            result.append({
                "id": t.id,
                "order_id": t.order_id,
                "user_id": t.user_id,
                "user_name": user_name,
                "order_number": order.order_number if order else "",
                "token_number": t.token_number,
                "status": t.status,
                "estimated_wait_minutes": t.estimated_wait_minutes,
                "queue_position": t.queue_position,
                "counter_number": t.counter_number,
                "items_summary": items_summary,
                "total_amount": order.final_amount if order else Decimal("0.0"),
                "called_at": t.called_at,
                "ready_at": t.ready_at,
                "completed_at": t.completed_at,
                "created_at": t.created_at,
                "updated_at": t.updated_at
            })
        return result

    @staticmethod
    def update_token_status(db: Session, token_id: int, update_in: TokenStatusUpdate) -> Token:
        """
        Updates token and corresponding order status through its lifecycle:
        Waiting -> Preparing -> Ready -> Completed / Cancelled.
        Triggers real-time notifications for the customer.
        """
        token = db.query(Token).filter(Token.id == token_id).first()
        if not token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found.")

        old_status = token.status
        new_status = update_in.status
        token.status = new_status
        token.updated_at = datetime.now()

        if update_in.counter_number:
            token.counter_number = update_in.counter_number

        # Update order status & timestamps
        order = token.order
        if order:
            if new_status == "Preparing":
                order.status = "Preparing"
                token.called_at = datetime.now()
                token.estimated_wait_minutes = max(3, token.estimated_wait_minutes - 5)
                # Send notification
                db.add(Notification(
                    user_id=token.user_id,
                    title="Order In Kitchen 🍳",
                    message=f"Chefs have started preparing your order for Token {token.token_number} at Counter {token.counter_number}.",
                    type="token",
                    reference_id=token.token_number
                ))
            elif new_status == "Ready":
                order.status = "Ready"
                token.ready_at = datetime.now()
                token.estimated_wait_minutes = 0
                token.queue_position = 0
                # Send alert notification
                db.add(Notification(
                    user_id=token.user_id,
                    title="Order Ready for Pickup! 🔔",
                    message=f"Your Token {token.token_number} is READY! Please collect your hot fresh food from Counter {token.counter_number}.",
                    type="token",
                    reference_id=token.token_number
                ))
            elif new_status == "Completed":
                order.status = "Completed"
                token.completed_at = datetime.now()
                token.estimated_wait_minutes = 0
                token.queue_position = 0
                # Send completion notification
                db.add(Notification(
                    user_id=token.user_id,
                    title="Order Completed ✨",
                    message=f"Token {token.token_number} completed. Thank you for dining at the Canteen!",
                    type="token",
                    reference_id=token.token_number
                ))
            elif new_status == "Cancelled":
                order.status = "Cancelled"
                token.estimated_wait_minutes = 0
                token.queue_position = 0
                db.add(Notification(
                    user_id=token.user_id,
                    title="Token Cancelled",
                    message=f"Your Token {token.token_number} was cancelled. Please speak with the counter manager.",
                    type="token",
                    reference_id=token.token_number
                ))

        db.commit()
        db.refresh(token)
        return token

    @staticmethod
    def verify_qr_payload(db: Session, qr_payload: str) -> dict:
        """
        Parses raw QR string or token number (e.g. 'TOKEN:C1-725|ORDER:12|USER:3' or 'C1-725' or '12')
        and returns verified order details with duplicate pickup checks.
        """
        raw = qr_payload.strip()
        token_num = None
        order_id = None

        if "TOKEN:" in raw:
            parts = raw.split("|")
            for p in parts:
                if p.startswith("TOKEN:"):
                    token_num = p.replace("TOKEN:", "").strip()
                elif p.startswith("ORDER:"):
                    try:
                        order_id = int(p.replace("ORDER:", "").strip())
                    except ValueError:
                        pass
        else:
            token_num = raw

        token = None
        if token_num:
            token = db.query(Token).filter(func.lower(Token.token_number) == func.lower(token_num)).first()
        if not token and order_id:
            token = db.query(Token).filter(Token.order_id == order_id).first()
        if not token and raw.isdigit():
            token = db.query(Token).filter(Token.id == int(raw)).first()

        if not token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid QR / Token: No matching order found for '{raw}'.")

        order = db.query(Order).filter(Order.id == token.order_id).first()
        user = order.user if order else None
        counter_name = f"Counter {token.counter_number} ({'South Indian Tiffin' if token.counter_number == 1 else ('Traditional Desserts' if token.counter_number == 2 else 'Beverages & Brews')})"

        items = []
        if order:
            for item in order.items:
                items.append({
                    "food_item_id": item.food_item_id,
                    "food_name": item.food_item.name if item.food_item else f"Dish #{item.food_item_id}",
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "subtotal": float(item.subtotal),
                    "special_instructions": item.special_instructions
                })

        is_already_collected = (token.status == "Completed")

        return {
            "is_valid": True,
            "token_id": token.id,
            "token_number": token.token_number,
            "counter_number": token.counter_number,
            "counter_name": counter_name,
            "order_id": order.id if order else token.order_id,
            "order_number": order.order_number if order else f"#ORD-{token.order_id}",
            "order_status": order.status if order else token.status,
            "token_status": token.status,
            "is_already_collected": is_already_collected,
            "student_name": user.name if user else "Campus Student",
            "student_email": user.email if user else "student@canteen.edu",
            "total_amount": float(order.final_amount) if order else 0.0,
            "payment_method": order.payment.payment_method if (order and order.payment) else "UPI",
            "items": items,
            "created_at": token.created_at.strftime("%I:%M %p, %b %d"),
            "ready_at": token.ready_at.strftime("%I:%M %p") if token.ready_at else None,
            "completed_at": token.completed_at.strftime("%I:%M %p") if token.completed_at else None
        }

    @staticmethod
    def mark_token_collected(db: Session, token_id: int) -> dict:
        """
        Staff action: marks a token and its order as Collected / Completed.
        Prevents duplicate pickups.
        """
        token = db.query(Token).filter(Token.id == token_id).first()
        if not token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found.")

        if token.status == "Completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate Pickup Alert: Token {token.token_number} has already been verified and collected at {token.completed_at.strftime('%I:%M %p') if token.completed_at else 'earlier'}!"
            )

        token.status = "Completed"
        token.completed_at = datetime.now()
        token.estimated_wait_minutes = 0
        token.queue_position = 0

        order = db.query(Order).filter(Order.id == token.order_id).first()
        if order:
            order.status = "Completed"
            db.add(Notification(
                user_id=order.user_id,
                title="Meal Picked Up ✅",
                message=f"Order for Token {token.token_number} verified and picked up from Counter {token.counter_number}. Enjoy your meal!",
                type="token",
                reference_id=token.token_number
            ))

        db.commit()
        db.refresh(token)

        return {
            "success": True,
            "token_number": token.token_number,
            "status": "Completed",
            "message": f"✅ Token {token.token_number} successfully verified and marked as COLLECTED!"
        }
