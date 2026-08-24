from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.models.user import User, Role
from backend.app.schemas.user import UserResponse, RoleResponse
from backend.app.authentication.deps import get_current_admin

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin endpoint: lists all registered users."""
    return db.query(User).order_by(User.id.asc()).all()

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    """Returns available roles in the system."""
    return db.query(Role).all()

@router.put("/{user_id}/status", response_model=UserResponse)
def toggle_user_status(user_id: int, is_active: bool, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin endpoint: activates or deactivates a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
