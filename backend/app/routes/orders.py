from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.order import Order
from backend.app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from backend.app.services.order_service import OrderService
from backend.app.authentication.deps import get_current_active_user, get_current_staff_or_admin

router = APIRouter(prefix="/api/orders", tags=["Orders"])

def _format_order_response(order: Order) -> OrderResponse:
    resp = OrderResponse.model_validate(order)
    if order.token:
        resp.token_number = order.token.token_number
        resp.token_status = order.token.status
        resp.estimated_wait_minutes = order.token.estimated_wait_minutes
        resp.queue_position = order.token.queue_position
        resp.counter_number = order.token.counter_number
    if order.payment:
        resp.payment_status = order.payment.status
        resp.payment_method = order.payment.payment_method
    return resp

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Places a new food order, validates inventory, charges payment, and generates a digital token.
    """
    result = OrderService.create_order(db=db, user_id=current_user.id, order_in=order_in)
    return _format_order_response(result["order"])

@router.get("/my-orders", response_model=List[OrderResponse])
@router.get("/me", response_model=List[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns order history for current logged-in student/user."""
    orders = OrderService.get_user_orders(db=db, user_id=current_user.id)
    return [_format_order_response(o) for o in orders]

@router.get("/admin/all", response_model=List[OrderResponse])
@router.get("/", response_model=List[OrderResponse])
def get_all_orders_admin(
    status_filter: Optional[str] = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
):
    """Admin/Staff endpoint: lists all orders with optional status filter."""
    orders = OrderService.get_all_orders(db=db, status_filter=status_filter)
    return [_format_order_response(o) for o in orders]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns single order details. Requires owner or staff/admin role."""
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    if order.user_id != current_user.id and current_user.role_id not in [1, 2]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to order.")
    return _format_order_response(order)

@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
):
    """Admin/Staff endpoint: updates status of an order."""
    order = OrderService.update_order_status(db=db, order_id=order_id, status_in=status_in)
    return _format_order_response(order)
