from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.models.notification import Notification
from backend.app.models.user import User
from backend.app.schemas.notification import NotificationCreate, NotificationBroadcast

class NotificationService:

    @staticmethod
    def get_user_notifications(db: Session, user_id: int) -> List[Notification]:
        return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(20).all()

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).count()

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> bool:
        db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
        db.commit()
        return True

    @staticmethod
    def mark_single_as_read(db: Session, notification_id: int, user_id: int) -> bool:
        notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
        if notif:
            notif.is_read = True
            db.commit()
            return True
        return False

    @staticmethod
    def create_notification(db: Session, notif_in: NotificationCreate) -> Notification:
        notif = Notification(
            user_id=notif_in.user_id,
            title=notif_in.title,
            message=notif_in.message,
            type=notif_in.type or "announcement",
            reference_id=notif_in.reference_id
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def broadcast_notification(db: Session, broadcast_in: NotificationBroadcast) -> int:
        """Sends a notification to all active students and staff."""
        users = db.query(User).filter(User.is_active == True).all()
        count = 0
        for u in users:
            notif = Notification(
                user_id=u.id,
                title=broadcast_in.title,
                message=broadcast_in.message,
                type=broadcast_in.type or "announcement",
                reference_id="BROADCAST"
            )
            db.add(notif)
            count += 1
        db.commit()
        return count
