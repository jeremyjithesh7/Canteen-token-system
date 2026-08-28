from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.app.models.payment import Payment
from backend.app.models.order import Order
from backend.app.schemas.payment import PaymentProcessRequest
from backend.app.utils.helpers import generate_transaction_id

class PaymentService:

    @staticmethod
    def process_payment_request(db: Session, user_id: int, payment_in: PaymentProcessRequest) -> Payment:
        """
        Initiates authentic payment transaction. Status remains 'Pending'
        until genuine verification (or completed atomically for Campus Wallet).
        """
        order = db.query(Order).filter(Order.id == payment_in.order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

        existing = db.query(Payment).filter(Payment.order_id == payment_in.order_id).first()
        if existing:
            return existing

        txn_id = generate_transaction_id()
        is_wallet = payment_in.payment_method == "Wallet"
        status_val = "Completed" if is_wallet else "Pending"

        payment = Payment(
            order_id=order.id,
            user_id=user_id,
            transaction_id=txn_id,
            payment_method=payment_in.payment_method,
            amount=payment_in.amount,
            status=status_val,
            gateway_response=f'{{"status": "{status_val}", "method": "{payment_in.payment_method}", "txn_id": "{txn_id}"}}'
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def get_payment_by_order(db: Session, order_id: int) -> Optional[Payment]:
        return db.query(Payment).filter(Payment.order_id == order_id).first()

    @staticmethod
    def get_all_payments(db: Session) -> List[Payment]:
        return db.query(Payment).order_by(Payment.created_at.desc()).all()
