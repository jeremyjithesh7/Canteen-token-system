from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.inventory import InventoryLog
from backend.app.schemas.inventory import InventoryResponse, InventoryUpdate, InventoryLogResponse
from backend.app.services.inventory_service import InventoryService
from backend.app.authentication.deps import get_current_staff_or_admin, get_current_admin

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

@router.get("/", response_model=List[InventoryResponse])
def get_inventory(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
):
    """Admin/Staff endpoint: returns stock levels across all dishes with low stock indicators."""
    items = InventoryService.get_all_inventory(db=db)
    return [InventoryResponse(**i) for i in items]

@router.get("/low-stock", response_model=List[InventoryResponse])
def get_low_stock(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
):
    """Admin/Staff endpoint: returns only items running below minimum stock threshold."""
    items = InventoryService.get_low_stock_items(db=db)
    return [InventoryResponse(**i) for i in items]

@router.put("/restock/{food_item_id}", response_model=InventoryResponse)
def restock_food_item(
    food_item_id: int,
    update_in: InventoryUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
):
    """Admin/Staff endpoint: restocks an item and records audit log."""
    inv = InventoryService.restock_item(db=db, food_item_id=food_item_id, update_in=update_in)
    food = inv.food_item
    return InventoryResponse(
        id=inv.id,
        food_item_id=inv.food_item_id,
        food_item_name=food.name if food else "",
        category_name=food.category.name if food and food.category else "",
        current_stock=inv.current_stock,
        minimum_stock_alert=inv.minimum_stock_alert,
        unit=inv.unit,
        is_low_stock=(inv.current_stock <= inv.minimum_stock_alert),
        last_restocked_at=inv.last_restocked_at,
        updated_at=inv.updated_at
    )

@router.get("/logs", response_model=List[InventoryLogResponse])
def get_inventory_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Admin endpoint: lists all stock change audit trails."""
    logs = db.query(InventoryLog).order_by(InventoryLog.created_at.desc()).limit(100).all()
    return logs
