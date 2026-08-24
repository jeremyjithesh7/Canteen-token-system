from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.user import UserCreate, UserLogin, TokenAuthResponse, UserResponse, RefreshTokenRequest
from backend.app.services.auth_service import AuthService
from backend.app.authentication.deps import get_current_active_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenAuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registers a new student account and returns JWT tokens."""
    return AuthService.register(db=db, user_data=user_data)

@router.post("/login", response_model=TokenAuthResponse)
def login_user(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticates credentials with rate-limiting and returns JWT access + refresh tokens."""
    client_ip = request.client.host if request.client else "unknown"
    return AuthService.login(db=db, credentials=credentials, client_ip=client_ip)

@router.post("/refresh", response_model=TokenAuthResponse)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Rotates refresh token and returns new JWT access token."""
    return AuthService.refresh_access_token(db=db, raw_refresh_token=data.refresh_token)

@router.post("/logout")
def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Revokes refresh token on user logout."""
    AuthService.revoke_refresh_token(db=db, raw_refresh_token=data.refresh_token)
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Returns the authenticated user profile with loyalty badge."""
    return AuthService.enrich_user_response(current_user, db)
