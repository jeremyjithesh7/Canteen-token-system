from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib

from backend.app.models.user import User, Role, RefreshToken
from backend.app.models.order import Order
from backend.app.schemas.user import UserCreate, UserLogin, TokenAuthResponse, UserResponse, RoleResponse
from backend.app.authentication.password import get_password_hash, verify_password
from backend.app.authentication.jwt import create_access_token, create_refresh_token, decode_token
from backend.app.authentication.rate_limiter import login_rate_limiter

class AuthService:
    @staticmethod
    def calculate_loyalty(orders_count: int) -> Dict[str, str]:
        if orders_count >= 25:
            return {"tier": "VIP Legend", "badge": "👑 Canteen VIP Legend"}
        elif orders_count >= 10:
            return {"tier": "Regular", "badge": "⭐ Canteen Regular"}
        elif orders_count >= 3:
            return {"tier": "Foodie", "badge": "🍔 Campus Foodie"}
        else:
            return {"tier": "Bronze", "badge": "🥉 Bronze Member"}

    @staticmethod
    def enrich_user_response(user: User, db: Session) -> UserResponse:
        orders_count = db.query(Order).filter(Order.user_id == user.id).count()
        loyalty = AuthService.calculate_loyalty(orders_count)
        
        role_resp = RoleResponse(id=user.role.id, name=user.role.name, description=user.role.description) if user.role else None
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            department=user.department,
            role_id=user.role_id,
            is_active=user.is_active,
            created_at=user.created_at,
            role=role_resp,
            loyalty_tier=loyalty["tier"],
            loyalty_badge=loyalty["badge"],
            total_orders_count=orders_count
        )

    @staticmethod
    def register(db: Session, user_data: UserCreate) -> TokenAuthResponse:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists."
            )

        hashed_pwd = get_password_hash(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            department=user_data.department,
            role_id=user_data.role_id or 3,
            password_hash=hashed_pwd,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        access_token = create_access_token(data={"sub": str(db_user.id), "email": db_user.email, "role": db_user.role_id})
        raw_refresh, token_hash, expires_at = create_refresh_token(user_id=db_user.id)
        
        # Save refresh token in DB
        db_refresh = RefreshToken(user_id=db_user.id, token_hash=token_hash, expires_at=expires_at)
        db.add(db_refresh)
        db.commit()

        user_resp = AuthService.enrich_user_response(db_user, db)
        return TokenAuthResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            user=user_resp
        )

    @staticmethod
    def login(db: Session, credentials: UserLogin, client_ip: str = "unknown") -> TokenAuthResponse:
        rate_key = f"{credentials.email}:{client_ip}"
        login_rate_limiter.check_rate_limit(rate_key)

        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.password_hash):
            login_rate_limiter.record_failure(rate_key)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Contact canteen administration."
            )

        login_rate_limiter.record_success(rate_key)

        access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role_id})
        raw_refresh, token_hash, expires_at = create_refresh_token(user_id=user.id)

        # Store refresh token
        db_refresh = RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
        db.add(db_refresh)
        db.commit()

        user_resp = AuthService.enrich_user_response(user, db)
        return TokenAuthResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            user=user_resp
        )

    @staticmethod
    def refresh_access_token(db: Session, raw_refresh_token: str) -> TokenAuthResponse:
        payload = decode_token(raw_refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = int(payload.get("sub"))
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()

        db_refresh = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False
        ).first()

        if not db_refresh or db_refresh.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

        # Rotate token
        db_refresh.revoked = True
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account inactive")

        new_access = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role_id})
        new_raw_refresh, new_hash, new_exp = create_refresh_token(user_id=user.id)
        
        new_db_refresh = RefreshToken(user_id=user.id, token_hash=new_hash, expires_at=new_exp)
        db.add(new_db_refresh)
        db.commit()

        user_resp = AuthService.enrich_user_response(user, db)
        return TokenAuthResponse(
            access_token=new_access,
            refresh_token=new_raw_refresh,
            token_type="bearer",
            user=user_resp
        )

    @staticmethod
    def revoke_refresh_token(db: Session, raw_refresh_token: str):
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).update({"revoked": True})
        db.commit()
