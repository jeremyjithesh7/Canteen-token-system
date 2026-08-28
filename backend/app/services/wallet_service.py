from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime

from backend.app.models.wallet import Wallet, WalletTransaction
from backend.app.models.user import User

class WalletService:
    @staticmethod
    def get_or_create_wallet(db: Session, user_id: int) -> Wallet:
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=Decimal("0.00"))
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        return wallet

    @staticmethod
    def get_wallet_summary(db: Session, user_id: int) -> dict:
        wallet = WalletService.get_or_create_wallet(db, user_id)
        txs = db.query(WalletTransaction).filter(WalletTransaction.wallet_id == wallet.id).order_by(WalletTransaction.created_at.desc()).limit(20).all()
        return {
            "balance": wallet.balance,
            "currency": "INR",
            "transactions": txs,
            "updated_at": wallet.updated_at
        }

    @staticmethod
    def top_up_wallet(db: Session, user_id: int, amount: Decimal, payment_reference: str = "Demo Top-Up") -> dict:
        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Top-up amount must be greater than zero.")

        wallet = WalletService.get_or_create_wallet(db, user_id)
        wallet.balance = wallet.balance + amount
        wallet.updated_at = datetime.utcnow()

        tx = WalletTransaction(
            wallet_id=wallet.id,
            user_id=user_id,
            amount=amount,
            transaction_type="CREDIT",
            description=f"Wallet Top-Up via {payment_reference}"
        )
        db.add(tx)
        db.commit()
        db.refresh(wallet)

        return {
            "balance": wallet.balance,
            "added_amount": amount,
            "message": f"Successfully added ₹{amount:.2f} to Campus Wallet!"
        }

    @staticmethod
    def deduct_wallet_for_order(db: Session, user_id: int, order_id: int, amount: Decimal) -> bool:
        wallet = WalletService.get_or_create_wallet(db, user_id)
        if wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient Campus Wallet balance (Available: ₹{wallet.balance:.2f}, Required: ₹{amount:.2f}). Please top up."
            )

        wallet.balance = wallet.balance - amount
        wallet.updated_at = datetime.utcnow()

        tx = WalletTransaction(
            wallet_id=wallet.id,
            user_id=user_id,
            amount=amount,
            transaction_type="DEBIT",
            description=f"Payment for Order #{order_id}",
            reference_order_id=order_id
        )
        db.add(tx)
        db.commit()
        return True
