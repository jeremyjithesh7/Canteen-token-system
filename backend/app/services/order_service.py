from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import json
import urllib.parse

from backend.app.config import settings
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
    def calculate_order_totals(db: Session, items_in: List[Any]) -> Dict[str, Any]:
        """
        Authoritative server-side price and tax calculator:
        Subtotal = sum(database price * quantity)
        5% Campus GST = round(subtotal * 0.05, 2)
        Final Total = Subtotal + GST
        """
        validated_items = []
        subtotal = Decimal("0.00")

        for item_in in items_in:
            food_item = db.query(FoodItem).filter(FoodItem.id == item_in.food_item_id).first()
            if not food_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Food item {item_in.food_item_id} not found.")
            if not food_item.is_available:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Food item '{food_item.name}' is currently unavailable.")
            if item_in.quantity <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid quantity {item_in.quantity} for '{food_item.name}'.")

            item_subtotal = (food_item.price * item_in.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            subtotal += item_subtotal

            validated_items.append({
                "food_item": food_item,
                "food_item_id": food_item.id,
                "quantity": item_in.quantity,
                "unit_price": food_item.price,
                "subtotal": item_subtotal,
                "special_instructions": getattr(item_in, "special_instructions", None)
            })

        gst_rate = Decimal(str(settings.CAMPUS_GST_PERCENT / 100.0))
        tax_amount = (subtotal * gst_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        final_amount = subtotal + tax_amount

        return {
            "validated_items": validated_items,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "final_amount": final_amount
        }

    @staticmethod
    def generate_upi_uri(amount: Decimal, order_number: str) -> str:
        """
        Generates standard dynamic UPI payment URI:
        upi://pay?pa={VPA}&pn={NAME}&am={AMOUNT}&tr={REF}&tn={NOTE}&cu=INR
        """
        vpa = settings.UPI_VPA
        name = settings.UPI_PAYEE_NAME
        amt_str = f"{amount:.2f}"
        note = f"Canteen Order #{order_number}"

        params = {
            "pa": vpa,
            "pn": name,
            "am": amt_str,
            "tr": order_number,
            "tn": note,
            "cu": "INR"
        }
        return f"upi://pay?{urllib.parse.urlencode(params)}"

    @staticmethod
    def create_order(db: Session, user_id: int, order_in: OrderCreate) -> Dict[str, Any]:
        """
        Processes order checkout with honest payment lifecycle:
        - Wallet: Deducts balance atomically -> Confirmed -> Token generated.
        - UPI / External: Sets Payment_Pending -> Generates UPI URI & QR data -> Waits for verification.
        """
        if not order_in.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain at least one item.")

        # 1. Server-side validation of items, prices, 5% GST and final amount
        calc = OrderService.calculate_order_totals(db=db, items_in=order_in.items)
        validated_items = calc["validated_items"]
        subtotal = calc["subtotal"]
        tax_amount = calc["tax_amount"]
        final_amount = calc["final_amount"]

        # 2. Deduct Inventory Stock
        order_number = generate_order_number()
        for item in validated_items:
            InventoryService.deduct_stock_for_order(
                db=db,
                food_item_id=item["food_item_id"],
                quantity=item["quantity"],
                order_number=order_number
            )

        # 3. Handle Payment Method & State
        payment_method = (order_in.payment_method or "UPI").strip()
        is_wallet = payment_method.lower() in ["wallet", "campus wallet"]

        if is_wallet:
            # Check wallet balance first
            wallet = WalletService.get_or_create_wallet(db, user_id)
            if wallet.balance < final_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient Campus Wallet balance (Available: ₹{wallet.balance:.2f}, Required: ₹{final_amount:.2f}). Please top up."
                )
            order_status = "Confirmed"
            payment_status = "Completed"
            payment_method_name = "Campus Wallet"
        else:
            # Honest UPI / External payment pending state
            order_status = "Payment_Pending"
            payment_status = "Pending"
            payment_method_name = "UPI" if payment_method.upper() == "UPI" else payment_method

        # 4. Create Order Record
        new_order = Order(
            user_id=user_id,
            order_number=order_number,
            total_amount=subtotal,
            discount_amount=Decimal("0.00"),
            final_amount=final_amount,
            status=order_status,
            notes=order_in.notes,
            scheduled_for=order_in.scheduled_for,
            is_preorder=order_in.is_preorder
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        if is_wallet:
            WalletService.deduct_wallet_for_order(db=db, user_id=user_id, order_id=new_order.id, amount=final_amount)

        # 5. Create Order Items
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

        # 6. Create Payment Record with UPI URI
        txn_id = generate_transaction_id()
        upi_uri = OrderService.generate_upi_uri(final_amount, order_number)

        gateway_info = {
            "status": payment_status,
            "upi_vpa": settings.UPI_VPA,
            "upi_payee_name": settings.UPI_PAYEE_NAME,
            "upi_uri": upi_uri,
            "amount": str(final_amount),
            "order_number": order_number,
            "created_at": datetime.now().isoformat()
        }

        payment = Payment(
            order_id=new_order.id,
            user_id=user_id,
            transaction_id=txn_id,
            payment_method=payment_method_name,
            amount=final_amount,
            status=payment_status,
            gateway_response=json.dumps(gateway_info)
        )
        db.add(payment)
        db.commit()

        # 7. Clear user's shopping cart
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()

        # 8. If Wallet payment was successful, issue digital token & rewards immediately
        token = None
        if is_wallet:
            token = TokenService.generate_token_for_order(db=db, order=new_order)
            RewardsService.process_order_rewards(db=db, user_id=user_id, order_amount=final_amount)

        db.refresh(new_order)
        return {
            "order": new_order,
            "token": token,
            "payment": payment,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "final_amount": final_amount,
            "upi_payment_uri": upi_uri,
            "upi_vpa": settings.UPI_VPA,
            "upi_payee_name": settings.UPI_PAYEE_NAME
        }

    @staticmethod
    def submit_payment_reference(db: Session, order_id: int, user_id: int, utr_reference: str) -> Order:
        """
        Records student-submitted UTR / Transaction reference for verification.
        Does NOT auto-confirm payment; remains Payment_Pending with reference logged.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        if payment:
            try:
                gw = json.loads(payment.gateway_response or "{}")
            except Exception:
                gw = {}
            gw["submitted_utr"] = utr_reference.strip()
            gw["utr_submitted_at"] = datetime.now().isoformat()
            payment.gateway_response = json.dumps(gw)
            db.commit()

        return order

    @staticmethod
    def confirm_payment_and_issue_token(db: Session, order_id: int) -> Order:
        """
        Genuine / Staff payment verification:
        Transitions Payment to Completed, Order to Confirmed, and generates Kitchen Token.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        if payment:
            payment.status = "Completed"

        order.status = "Confirmed"
        order.updated_at = datetime.now()
        db.commit()

        # Issue token for kitchen preparation
        TokenService.generate_token_for_order(db=db, order=order)
        RewardsService.process_order_rewards(db=db, user_id=order.user_id, order_amount=order.final_amount)

        db.refresh(order)
        return order

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
