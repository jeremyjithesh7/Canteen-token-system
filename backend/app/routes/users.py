from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database.session import get_db
from backend.app.models.user import User, Role
from backend.app.models.ai_data import UserPreference
from backend.app.schemas.user import UserResponse, RoleResponse, UserPreferenceUpdate, UserPreferenceResponse
from backend.app.authentication.deps import get_current_admin, get_current_active_user
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Returns the authenticated user profile with loyalty badge."""
    return AuthService.enrich_user_response(current_user, db)

@router.get("/me/preferences", response_model=Optional[UserPreferenceResponse])
def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Returns dietary & recommendation preferences for current user."""
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    return pref

@router.put("/me/preferences", response_model=UserPreferenceResponse)
def update_user_preferences(
    pref_in: UserPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Updates dietary & recommendation preferences for current user."""
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(
            user_id=current_user.id,
            favorite_category_id=pref_in.favorite_category_id,
            is_veg_only=pref_in.is_veg_only,
            spice_level=pref_in.spice_level or "Medium",
            dietary_notes=pref_in.dietary_notes
        )
        db.add(pref)
    else:
        if pref_in.favorite_category_id is not None:
            pref.favorite_category_id = pref_in.favorite_category_id
        if pref_in.is_veg_only is not None:
            pref.is_veg_only = pref_in.is_veg_only
        if pref_in.spice_level is not None:
            pref.spice_level = pref_in.spice_level
        if pref_in.dietary_notes is not None:
            pref.dietary_notes = pref_in.dietary_notes
    db.commit()
    db.refresh(pref)
    return pref

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
