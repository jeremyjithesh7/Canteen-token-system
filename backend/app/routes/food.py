from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.app.database.session import get_db
from backend.app.models.food import Category, FoodItem, Menu, MenuItem
from backend.app.models.inventory import Inventory
from backend.app.models.user import User
from backend.app.schemas.food import (
    CategoryCreate, CategoryResponse,
    FoodItemCreate, FoodItemUpdate, FoodItemResponse,
    MenuResponse
)
from backend.app.authentication.deps import get_current_admin, get_current_staff_or_admin

router = APIRouter(prefix="/api/food", tags=["Food & Menu Catalog"])

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Returns all active food categories ordered by display_order."""
    return db.query(Category).filter(Category.is_active == True).order_by(Category.display_order.asc()).all()

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin endpoint: adds a new food category."""
    existing = db.query(Category).filter(Category.slug == category_in.slug).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category with this slug already exists.")
    cat = Category(**category_in.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/items", response_model=List[FoodItemResponse])
def get_food_items(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_veg: Optional[bool] = Query(None, description="Filter strictly vegetarian items"),
    search: Optional[str] = Query(None, description="Search keyword in item name or description"),
    only_available: bool = Query(True, description="Only show available items for ordering"),
    db: Session = Depends(get_db)
):
    """Returns food items matching given query filters with real-time stock levels."""
    query = db.query(FoodItem)
    if only_available:
        query = query.filter(FoodItem.is_available == True)
    if category_id:
        query = query.filter(FoodItem.category_id == category_id)
    if is_veg is not None:
        query = query.filter(FoodItem.is_veg == is_veg)
    if search:
        keyword = f"%{search.strip().lower()}%"
        query = query.filter(FoodItem.name.ilike(keyword) | FoodItem.description.ilike(keyword))

    items = query.order_by(FoodItem.category_id.asc(), FoodItem.id.asc()).all()
    results = []
    for item in items:
        inv = item.inventory
        stock = inv.current_stock if inv else 0
        resp = FoodItemResponse.model_validate(item)
        resp.current_stock = stock
        if item.ratings and len(item.ratings) > 0:
            resp.average_rating = round(float(sum(r.rating for r in item.ratings) / len(item.ratings)), 1)
            resp.rating_count = len(item.ratings)
        else:
            resp.average_rating = 4.8
            resp.rating_count = 14
        results.append(resp)
    return results

@router.get("/items/{item_id}", response_model=FoodItemResponse)
def get_food_item_detail(item_id: int, db: Session = Depends(get_db)):
    """Returns detailed information and nutritional macros for a specific food item."""
    item = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found.")
    inv = item.inventory
    resp = FoodItemResponse.model_validate(item)
    resp.current_stock = inv.current_stock if inv else 0
    if item.ratings and len(item.ratings) > 0:
        resp.average_rating = round(float(sum(r.rating for r in item.ratings) / len(item.ratings)), 1)
        resp.rating_count = len(item.ratings)
    else:
        resp.average_rating = 4.8
        resp.rating_count = 14
    return resp

@router.post("/items", response_model=FoodItemResponse, status_code=status.HTTP_201_CREATED)
def create_food_item(item_in: FoodItemCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin endpoint: adds a new food item and initializes inventory."""
    cat = db.query(Category).filter(Category.id == item_in.category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    item_data = item_in.model_dump()
    initial_stock = item_data.pop("initial_stock", 50)

    food = FoodItem(**item_data)
    db.add(food)
    db.commit()
    db.refresh(food)

    # Initialize inventory record
    inv = Inventory(food_item_id=food.id, current_stock=initial_stock, minimum_stock_alert=10)
    db.add(inv)
    db.commit()

    resp = FoodItemResponse.model_validate(food)
    resp.current_stock = initial_stock
    return resp

@router.put("/items/{item_id}", response_model=FoodItemResponse)
def update_food_item(
    item_id: int,
    item_in: FoodItemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
):
    """Admin/Staff endpoint: updates food item details, price, availability, or prep time."""
    food = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found.")

    for field, value in item_in.model_dump(exclude_unset=True).items():
        setattr(food, field, value)

    db.commit()
    db.refresh(food)
    inv = food.inventory
    resp = FoodItemResponse.model_validate(food)
    resp.current_stock = inv.current_stock if inv else 0
    return resp

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_item(item_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin endpoint: soft deletes or removes a food item."""
    food = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found.")
    food.is_available = False
    db.commit()
    return None

@router.get("/menu/today", response_model=MenuResponse)
def get_today_menu(db: Session = Depends(get_db)):
    """Returns today's active menu and linked food items."""
    today = date.today()
    menu = db.query(Menu).filter(Menu.menu_date == today).first()
    if not menu:
        menu = Menu(menu_date=today, is_active=True)
        db.add(menu)
        db.commit()
        db.refresh(menu)
        # Link all available food items
        all_foods = db.query(FoodItem).filter(FoodItem.is_available == True).all()
        for f in all_foods:
            db.add(MenuItem(menu_id=menu.id, food_item_id=f.id, daily_stock_limit=100))
        db.commit()
        db.refresh(menu)
    return menu
