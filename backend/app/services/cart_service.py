from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict, Any

from backend.app.models.cart import CartItem
from backend.app.models.food import FoodItem
from backend.app.schemas.cart import CartItemPayload, CartItemDetail, CartSummaryResponse

class CartService:
    @staticmethod
    def get_user_cart(db: Session, user_id: int) -> CartSummaryResponse:
        cart_rows = db.query(CartItem).filter(CartItem.user_id == user_id).all()
        details: List[CartItemDetail] = []
        subtotal = Decimal("0.00")
        total_items_count = 0

        for row in cart_rows:
            food = db.query(FoodItem).filter(FoodItem.id == row.food_item_id).first()
            if not food:
                continue

            stock = food.inventory.current_stock if food.inventory else 50
            item_subtotal = Decimal(str(food.price)) * row.quantity
            subtotal += item_subtotal
            total_items_count += row.quantity

            details.append(CartItemDetail(
                id=row.id,
                food_item_id=food.id,
                name=food.name,
                price=Decimal(str(food.price)),
                quantity=row.quantity,
                subtotal=item_subtotal,
                image_url=food.image_url,
                counter_id=food.counter_id or 1,
                category_name=food.category.name if food.category else "Specialty",
                is_veg=food.is_veg,
                prep_time_minutes=food.prep_time_minutes,
                is_available=food.is_available,
                current_stock=stock,
                special_notes=row.special_notes
            ))

        # 5% Canteen GST
        gst_tax = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
        grand_total = subtotal + gst_tax

        return CartSummaryResponse(
            items=details,
            total_items_count=total_items_count,
            subtotal=subtotal,
            gst_tax_amount=gst_tax,
            grand_total=grand_total
        )

    @staticmethod
    def sync_cart(db: Session, user_id: int, items_payload: List[CartItemPayload]) -> CartSummaryResponse:
        # Clear existing server cart for user and replace with client state
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        for item in items_payload:
            food = db.query(FoodItem).filter(FoodItem.id == item.food_item_id).first()
            if food and food.is_available:
                new_row = CartItem(
                    user_id=user_id,
                    food_item_id=item.food_item_id,
                    quantity=item.quantity,
                    special_notes=item.special_notes
                )
                db.add(new_row)
        db.commit()
        return CartService.get_user_cart(db, user_id)

    @staticmethod
    def add_or_update_item(db: Session, user_id: int, food_item_id: int, quantity: int, notes: str = None) -> CartSummaryResponse:
        existing = db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.food_item_id == food_item_id
        ).first()

        if quantity <= 0:
            if existing:
                db.delete(existing)
                db.commit()
        else:
            if existing:
                existing.quantity = quantity
                if notes is not None:
                    existing.special_notes = notes
            else:
                new_item = CartItem(
                    user_id=user_id,
                    food_item_id=food_item_id,
                    quantity=quantity,
                    special_notes=notes
                )
                db.add(new_item)
            db.commit()

        return CartService.get_user_cart(db, user_id)

    @staticmethod
    def remove_item(db: Session, user_id: int, food_item_id: int) -> CartSummaryResponse:
        db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.food_item_id == food_item_id
        ).delete()
        db.commit()
        return CartService.get_user_cart(db, user_id)

    @staticmethod
    def clear_cart(db: Session, user_id: int) -> CartSummaryResponse:
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()
        return CartService.get_user_cart(db, user_id)
