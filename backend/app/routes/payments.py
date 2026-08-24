from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.payment import PaymentProcessRequest, PaymentResponse
from backend.app.services.payment_service import PaymentService
from backend.app.authentication.deps import get_current_active_user, get_current_admin

router = APIRouter(prefix="/api/payments", tags=["Payments (Demo Gateway)"])

@router.post("/process", response_model=PaymentResponse)
def process_payment(
    payment_in: PaymentProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Processes simulated instant payment confirmation via demo gateway."""
    return PaymentService.process_demo_payment(db=db, user_id=current_user.id, payment_in=payment_in)

@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_payment_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns payment confirmation details for a specific order."""
    payment = PaymentService.get_payment_by_order(db=db, order_id=order_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found.")
    return payment

@router.get("/", response_model=List[PaymentResponse])
def get_all_payments_admin(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Admin endpoint: lists all historical payment transactions."""
    return PaymentService.get_all_payments(db=db)
