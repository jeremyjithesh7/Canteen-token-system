from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class WalletTopUpRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, le=5000, description="Top-up amount in INR")
    payment_reference: Optional[str] = "Demo Campus Top-Up"

class WalletTransactionResponse(BaseModel):
    id: int
    amount: Decimal
    transaction_type: str
    description: str
    reference_order_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class WalletResponse(BaseModel):
    balance: Decimal
    currency: str = "INR"
    transactions: List[WalletTransactionResponse] = []
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
