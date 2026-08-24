from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict, Any

from backend.app.database.session import get_db
from backend.app.schemas.wallet import WalletResponse, WalletTopUpRequest
from backend.app.services.wallet_service import WalletService
from backend.app.authentication.deps import get_current_active_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/wallet", tags=["Campus Wallet"])

@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns current student campus wallet balance and recent transaction history."""
    return WalletService.get_wallet_summary(db=db, user_id=current_user.id)

@router.post("/topup")
def top_up_my_wallet(
    data: WalletTopUpRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Adds simulated demo balance to student campus wallet."""
    return WalletService.top_up_wallet(
        db=db,
        user_id=current_user.id,
        amount=data.amount,
        payment_reference=data.payment_reference or "Demo Instant Top-Up"
    )
