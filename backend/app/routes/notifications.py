from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.notification import NotificationResponse, NotificationBroadcast
from backend.app.services.notification_service import NotificationService
from backend.app.authentication.deps import get_current_active_user, get_current_admin

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns recent in-app notifications for current user."""
    return NotificationService.get_user_notifications(db=db, user_id=current_user.id)

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, int]:
    """Returns count of unread notifications for badge icon."""
    count = NotificationService.get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}

@router.put("/mark-all-read")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, bool]:
    """Marks all user notifications as read."""
    success = NotificationService.mark_all_as_read(db=db, user_id=current_user.id)
    return {"success": success}

@router.put("/{notification_id}/read")
def mark_single_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, bool]:
    """Marks a single notification as read."""
    success = NotificationService.mark_single_as_read(db=db, notification_id=notification_id, user_id=current_user.id)
    return {"success": success}

@router.post("/broadcast")
def broadcast_announcement(
    broadcast_in: NotificationBroadcast,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Admin endpoint: broadcasts an announcement to all students & staff."""
    sent_count = NotificationService.broadcast_notification(db=db, broadcast_in=broadcast_in)
    return {"message": "Announcement broadcast successfully.", "recipients_count": sent_count}
