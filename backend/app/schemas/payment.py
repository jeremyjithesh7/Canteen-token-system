from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentProcessRequest(BaseModel):
    order_id: int
    payment_method: str = "UPI" # 'Card', 'UPI', 'Wallet', 'NetBanking', 'Cash'
    amount: Decimal = Field(..., ge=0)
    card_number: Optional[str] = None
    upi_id: Optional[str] = None
    wallet_type: Optional[str] = None

PaymentCreate = PaymentProcessRequest

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    transaction_id: str
    payment_method: str
    amount: Decimal
    status: str
    gateway_response: Optional[str] = None
    payment_date: datetime

    class Config:
        from_attributes = True
