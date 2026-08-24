from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.app.models.inventory import Inventory, InventoryLog
from backend.app.models.food import FoodItem
from backend.app.schemas.inventory import InventoryUpdate

class InventoryService:

    @staticmethod
    def get_all_inventory(db: Session) -> List[Dict[str, Any]]:
        """Retrieves inventory status across all food items with low stock calculation."""
        records = db.query(Inventory, FoodItem).join(FoodItem, Inventory.food_item_id == FoodItem.id).all()
        results = []
        for inv, food in records:
            is_low = inv.current_stock <= inv.minimum_stock_alert
            results.append({
                "id": inv.id,
                "food_item_id": inv.food_item_id,
                "food_item_name": food.name,
                "category_name": food.category.name if food.category else "Uncategorized",
                "current_stock": inv.current_stock,
                "minimum_stock_alert": inv.minimum_stock_alert,
                "unit": inv.unit,
                "is_low_stock": is_low,
                "last_restocked_at": inv.last_restocked_at,
                "updated_at": inv.updated_at
            })
        return sorted(results, key=lambda x: (not x["is_low_stock"], x["current_stock"]))

    @staticmethod
    def get_low_stock_items(db: Session) -> List[Dict[str, Any]]:
        """Returns items where current_stock <= minimum_stock_alert."""
        all_inv = InventoryService.get_all_inventory(db)
        return [item for item in all_inv if item["is_low_stock"]]

    @staticmethod
    def restock_item(db: Session, food_item_id: int, update_in: InventoryUpdate) -> Inventory:
        """Restocks or updates stock level for a food item and logs the audit trail."""
        inv = db.query(Inventory).filter(Inventory.food_item_id == food_item_id).first()
        if not inv:
            inv = Inventory(
                food_item_id=food_item_id,
                current_stock=0,
                minimum_stock_alert=update_in.minimum_stock_alert or 10
            )
            db.add(inv)

        old_stock = inv.current_stock
        if update_in.add_quantity is not None:
            inv.current_stock += update_in.add_quantity
            change = update_in.add_quantity
        elif update_in.current_stock is not None:
            change = update_in.current_stock - old_stock
            inv.current_stock = update_in.current_stock
        else:
            change = 0

        if update_in.minimum_stock_alert is not None:
            inv.minimum_stock_alert = update_in.minimum_stock_alert

        inv.last_restocked_at = datetime.now()
        
        # Log inventory event
        if change != 0:
            log = InventoryLog(
                food_item_id=food_item_id,
                change_amount=change,
                reason=update_in.reason or "Restock",
                reference_id=f"RESTOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            db.add(log)

        # Update food item availability flag if stock restored
        food_item = db.query(FoodItem).filter(FoodItem.id == food_item_id).first()
        if food_item and inv.current_stock > 0:
            food_item.is_available = True

        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def deduct_stock_for_order(db: Session, food_item_id: int, quantity: int, order_number: str) -> bool:
        """Deducts stock when an order is confirmed and marks out-of-stock if depleted."""
        inv = db.query(Inventory).filter(Inventory.food_item_id == food_item_id).first()
        if not inv:
            return True # If untracked, continue

        if inv.current_stock < quantity:
            food = db.query(FoodItem).filter(FoodItem.id == food_item_id).first()
            name = food.name if food else f"Item #{food_item_id}"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sorry, '{name}' is out of stock or does not have sufficient quantity (Available: {inv.current_stock})."
            )

        inv.current_stock -= quantity
        log = InventoryLog(
            food_item_id=food_item_id,
            change_amount=-quantity,
            reason="order_placed",
            reference_id=order_number
        )
        db.add(log)

        # Auto toggle availability if 0 stock
        if inv.current_stock <= 0:
            food = db.query(FoodItem).filter(FoodItem.id == food_item_id).first()
            if food:
                food.is_available = False

        db.commit()
        return True
