from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.schemas.cart import (
    CartItemPayload,
    CartItemUpdate,
    CartSummaryResponse,
    CartSyncPayload
)
from backend.app.services.cart_service import CartService
from backend.app.authentication.deps import get_current_active_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/cart", tags=["Cart Management"])

@router.get("/", response_model=CartSummaryResponse)
@router.get("/me", response_model=CartSummaryResponse)
def get_user_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Fetch logged-in user's active cart with real-time price & stock calculations."""
    return CartService.get_user_cart(db=db, user_id=current_user.id)

@router.post("/sync", response_model=CartSummaryResponse)
def sync_cart(
    payload: CartSyncPayload,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Synchronize client-side cart items into server database session."""
    return CartService.sync_cart(db=db, user_id=current_user.id, items_payload=payload.items)

@router.post("/items", response_model=CartSummaryResponse)
def add_or_update_item(
    payload: CartItemPayload,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add or adjust food item quantity in persistent cart."""
    return CartService.add_or_update_item(
        db=db,
        user_id=current_user.id,
        food_item_id=payload.food_item_id,
        quantity=payload.quantity,
        notes=payload.special_notes
    )

@router.delete("/items/{food_item_id}", response_model=CartSummaryResponse)
def remove_cart_item(
    food_item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a specific food item from the cart."""
    return CartService.remove_item(db=db, user_id=current_user.id, food_item_id=food_item_id)

@router.delete("/", response_model=CartSummaryResponse)
def clear_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear all items in the user's cart."""
    return CartService.clear_cart(db=db, user_id=current_user.id)
