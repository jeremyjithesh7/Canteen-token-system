from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.token import Token
from backend.app.models.counter import Counter
from backend.app.schemas.token import TokenResponse, TokenStatusUpdate, LiveQueueStatus
from backend.app.services.token_service import TokenService
from backend.app.services.ai_service import AIService
from backend.app.authentication.deps import get_current_active_user, get_current_staff_or_admin

router = APIRouter(prefix="/api/tokens", tags=["Digital Tokens & Queue"])

def _format_token_response(t: Token) -> TokenResponse:
    order = t.order
    user_name = order.user.name if order and order.user else (t.user.name if t.user else "Customer")
    items_summary = ", ".join([f"{item.quantity}x {item.food_item.name}" for item in order.items if item.food_item]) if order else ""
    return TokenResponse(
        id=t.id,
        order_id=t.order_id,
        user_id=t.user_id,
        token_number=t.token_number,
        status=t.status,
        estimated_wait_minutes=t.estimated_wait_minutes,
        queue_position=t.queue_position,
        priority_score=t.priority_score,
        counter_number=t.counter_number,
        order_number=order.order_number if order else "",
        user_name=user_name,
        items_summary=items_summary,
        total_amount=order.final_amount if order else None,
        called_at=t.called_at,
        ready_at=t.ready_at,
        completed_at=t.completed_at,
        created_at=t.created_at,
        updated_at=t.updated_at
    )

@router.get("/active/me", response_model=Optional[TokenResponse])
def get_my_active_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns the most recent active token ('Waiting', 'Preparing', 'Ready') for the logged in user."""
    token = db.query(Token).filter(
        Token.user_id == current_user.id,
        Token.status.in_(["Waiting", "Preparing", "Ready"])
    ).order_by(Token.id.desc()).first()

    if not token:
        # If no active token, return latest token
        latest = db.query(Token).filter(Token.user_id == current_user.id).order_by(Token.id.desc()).first()
        if latest:
            return _format_token_response(latest)
        return None

    return _format_token_response(token)

@router.get("/my-tokens", response_model=List[TokenResponse])
def get_all_my_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns all tokens ever issued to the user."""
    tokens = TokenService.get_user_tokens(db=db, user_id=current_user.id)
    return [_format_token_response(t) for t in tokens]

@router.get("/live-board", response_model=List[TokenResponse])
def get_live_queue_board(db: Session = Depends(get_db)):
    """Public/Student endpoint: returns currently active tokens on the kitchen queue board."""
    tokens_data = TokenService.get_live_queue(db=db)
    return [TokenResponse(**t) for t in tokens_data]

@router.get("/kiosk/live")
def get_kiosk_live_board(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Kiosk Big-Screen Display Feed:
    Returns 'Now Serving' (Ready) tokens and 'Next Up' (Preparing / Waiting) tokens per counter.
    """
    counters = db.query(Counter).filter(Counter.is_active == True).order_by(Counter.id.asc()).all()
    counter_boards = []

    for c in counters:
        now_serving = db.query(Token).filter(
            Token.counter_number == c.id,
            Token.status == "Ready"
        ).order_by(Token.updated_at.desc()).first()

        preparing = db.query(Token).filter(
            Token.counter_number == c.id,
            Token.status == "Preparing"
        ).order_by(Token.id.asc()).limit(3).all()

        waiting = db.query(Token).filter(
            Token.counter_number == c.id,
            Token.status == "Waiting"
        ).order_by(Token.id.asc()).limit(4).all()

        counter_boards.append({
            "counter_id": c.id,
            "counter_name": c.name,
            "counter_code": c.code,
            "station_type": c.station_type,
            "now_serving": now_serving.token_number if now_serving else None,
            "now_serving_id": now_serving.id if now_serving else None,
            "next_up": [t.token_number for t in preparing + waiting]
        })

    # AI Crowd prediction status
    queue_status = AIService.get_live_queue_and_crowd_status(db=db)

    return {
        "counters": counter_boards,
        "crowd_level": queue_status.crowd_level,
        "estimated_wait_minutes": queue_status.estimated_average_wait_minutes,
        "total_waiting_tokens": queue_status.total_active_orders
    }

@router.post("/verify-qr")
@router.get("/verify-qr")
def verify_qr_token(
    qr_payload: str = None,
    token_str: Optional[str] = None,
    db: Session = Depends(get_db),
    staff_or_admin: User = Depends(get_current_staff_or_admin)
):
    """
    Staff tool: verifies student QR code or token string, returns items, counter, customer, and duplicate check.
    """
    payload = qr_payload or token_str
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a QR payload or token number.")
    return TokenService.verify_qr_payload(db=db, qr_payload=payload)

@router.post("/{token_id}/mark-collected")
def mark_token_collected(
    token_id: int,
    db: Session = Depends(get_db),
    staff_or_admin: User = Depends(get_current_staff_or_admin)
):
    """
    Staff tool: marks a token as Collected / Completed and prevents duplicate collection.
    """
    return TokenService.mark_token_collected(db=db, token_id=token_id)

@router.get("/{token_id}", response_model=TokenResponse)
def get_token_detail(token_id: int, db: Session = Depends(get_db)):
    """Returns single token details."""
    token = TokenService.get_token_by_id(db=db, token_id=token_id)
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found.")
    return _format_token_response(token)

@router.put("/{token_id}/status", response_model=TokenResponse)
def update_token_status(
    token_id: int,
    status_in: TokenStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_staff_or_admin)
):
    """
    Admin/Kitchen Staff endpoint: transitions token through its lifecycle:
    Waiting -> Preparing -> Ready -> Completed / Cancelled.
    """
    token = TokenService.update_token_status(db=db, token_id=token_id, update_in=status_in)
    return _format_token_response(token)
