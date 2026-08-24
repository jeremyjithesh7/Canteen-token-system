import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import uuid
from backend.app.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Encodes a JWT access token with user payload."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> (str, str, datetime):
    """
    Creates a long-lived JWT refresh token with unique JTI.
    Returns (raw_token, token_hash, expires_at).
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    payload = {
        "sub": str(user_id),
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "type": "refresh"
    }
    raw_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token, token_hash, expire

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Alias for backward compatibility
decode_access_token = decode_token
