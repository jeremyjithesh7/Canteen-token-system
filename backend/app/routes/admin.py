from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import io
import csv

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.order import Order, OrderItem
from backend.app.models.token import Token
from backend.app.models.food import FoodItem
from backend.app.models.counter import Counter
from backend.app.models.inventory import Inventory
from backend.app.authentication.deps import get_current_staff_or_admin, get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

@router.get("/dashboard-stats")
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
) -> Dict[str, Any]:
    today_start = datetime.combine(date.today(), datetime.min.time())

    # Total revenue today
    today_orders = db.query(Order).filter(Order.created_at >= today_start, Order.status != "Cancelled").all()
    today_revenue = sum(o.final_amount for o in today_orders)
    total_orders_today = len(today_orders)

    # Active tokens
    active_tokens = db.query(Token).filter(Token.status.in_(["Waiting", "Preparing"])).all()
    waiting_tokens_count = sum(1 for t in active_tokens if t.status == "Waiting")
    preparing_tokens_count = sum(1 for t in active_tokens if t.status == "Preparing")
    ready_tokens_count = db.query(Token).filter(Token.status == "Ready").count()

    # Low stock items count
    low_stock_count = db.query(Inventory).filter(Inventory.current_stock <= Inventory.minimum_stock_alert).count()

    # Total active menu items
    total_items_count = db.query(FoodItem).filter(FoodItem.is_available == True).count()

    # Status distribution
    status_counts = {
        "Waiting": waiting_tokens_count,
        "Preparing": preparing_tokens_count,
        "Ready": ready_tokens_count,
        "Completed": db.query(Token).filter(Token.status == "Completed").count(),
        "Cancelled": db.query(Token).filter(Token.status == "Cancelled").count()
    }

    # Top selling items
    top_items_query = (
        db.query(FoodItem.name, func.sum(OrderItem.quantity).label("total_qty"), func.sum(OrderItem.subtotal).label("total_sales"))
        .join(OrderItem, FoodItem.id == OrderItem.food_item_id)
        .group_by(FoodItem.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )
    top_items = [
        {"name": row[0], "quantity_sold": int(row[1] or 0), "revenue": float(row[2] or 0.0)}
        for row in top_items_query
    ]

    # Daily revenue past 7 days
    revenue_chart_labels = []
    revenue_chart_data = []
    for d in range(6, -1, -1):
        day = date.today() - timedelta(days=d)
        d_start = datetime.combine(day, datetime.min.time())
        d_end = datetime.combine(day, datetime.max.time())
        day_rev = db.query(func.sum(Order.final_amount)).filter(
            Order.created_at >= d_start,
            Order.created_at <= d_end,
            Order.status != "Cancelled"
        ).scalar() or 0.0
        revenue_chart_labels.append(day.strftime("%b %d"))
        revenue_chart_data.append(float(day_rev))

    # Peak order hours dynamically computed from recent order history
    past_week_start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    recent_orders = db.query(Order.created_at).filter(
        Order.created_at >= past_week_start,
        Order.status != "Cancelled"
    ).all()

    hour_counts = {h: 0 for h in range(8, 21)}
    for (order_dt,) in recent_orders:
        if order_dt:
            h = order_dt.hour
            if h in hour_counts:
                hour_counts[h] += 1

    peak_hours_data = [
        {"hour": f"{h:02d}:00", "orders": count}
        for h, count in sorted(hour_counts.items())
    ]

    return {
        "today_revenue": float(today_revenue),
        "total_orders_today": total_orders_today,
        "active_queue_count": len(active_tokens),
        "waiting_count": waiting_tokens_count,
        "preparing_count": preparing_tokens_count,
        "ready_count": ready_tokens_count,
        "low_stock_count": low_stock_count,
        "total_menu_items": total_items_count,
        "status_distribution": status_counts,
        "top_selling_items": top_items,
        "revenue_trends": {
            "labels": revenue_chart_labels,
            "data": revenue_chart_data
        },
        "peak_hours": peak_hours_data
    }

@router.get("/export-sales")
def export_sales_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    format: str = Query("csv", pattern="^(csv|excel)$"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Exports comprehensive sales report CSV including order list, totals, and per-counter breakdowns.
    """
    start = datetime.combine(start_date or (date.today() - timedelta(days=30)), datetime.min.time())
    end = datetime.combine(end_date or date.today(), datetime.max.time())

    orders = db.query(Order).filter(Order.created_at >= start, Order.created_at <= end).order_by(Order.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header section
    writer.writerow(["DIGITAL CANTEEN TOKEN SYSTEM - SALES REPORT"])
    writer.writerow(["Period", f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"])
    writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["Generated By", f"{admin.name} ({admin.email})"])
    writer.writerow([])

    # Metrics Summary
    total_sales = sum(o.final_amount for o in orders if o.status != "Cancelled")
    writer.writerow(["SUMMARY METRICS"])
    writer.writerow(["Total Orders", len(orders)])
    writer.writerow(["Total Revenue (INR)", f"{total_sales:.2f}"])
    writer.writerow([])

    # Table of Orders
    writer.writerow(["Order Number", "Date", "Customer ID", "Items Ordered", "Total Amount (INR)", "Payment Method", "Status", "Token Number", "Counter"])
    for o in orders:
        token = o.token
        items_str = "; ".join([f"{item.quantity}x {item.food_item.name if item.food_item else 'Dish'}" for item in o.items])
        writer.writerow([
            o.order_number,
            o.created_at.strftime("%Y-%m-%d %H:%M"),
            o.user_id,
            items_str,
            f"{o.final_amount:.2f}",
            o.payment.payment_method if o.payment else "UPI",
            o.status,
            token.token_number if token else "-",
            f"Counter {token.counter_number}" if token else "-"
        ])

    csv_data = output.getvalue()
    filename = f"canteen_sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
