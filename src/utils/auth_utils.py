from datetime import UTC, timedelta
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status, Depends
import jwt 
import bcrypt
from src.auth.models import User
from src.config.database import get_db
from src.config.setting import settings
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from src.utils.auth_bearer import JWTBearer

def hash_password(password: str):
    """Transfrom and return plain text password into hashed password."""

    hashed_pwd = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    return hashed_pwd.decode("utf-8")


def verify_password(password: str, hashed_password: str):
    """Check if provided password matches with saved password hash."""

    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))





def encode_access_token(
    username: str,
    expires_delta: timedelta | None = settings.ACCESS_TOKEN_EXPIRES_AT,
):
    """Create access token from provided data."""

    payload = {
        "exp": datetime.now(UTC) + timedelta(minutes=expires_delta),
        "iat": datetime.now(UTC),
        "scope": "access_token",
        "sub": username,
    }

    return jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)



def decode_access_token(token: str):
    """Decode access token."""

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, [settings.JWT_ALGORITHM])

        if payload["scope"] == "access_token":
            return payload

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Scope for the token invalid",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def encode_refresh_token(
    username: str,
    expires_delta: timedelta | None = settings.REFRESH_TOKEN_EXPIRES_AT,
):
    """Create refresh token from access token."""

    payload = {
        "exp": datetime.now(UTC) + timedelta(minutes=expires_delta),
        "iat": datetime.now(UTC),
        "scope": "refresh_token",
        "sub": username,
    }

    return jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)


def get_new_access_token(refresh_token: str):
    """Issue new access token from valid refresh token."""

    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, [settings.JWT_ALGORITHM]
        )

        if payload["scope"] == "refresh_token":
            user_data = payload["sub"]
            new_token = encode_access_token(user_data)
            return new_token

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid scope for the token",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


def verify_jwt(token: str, db: Session) -> bool:
    is_token_valid: bool = False

    try:
        payload = decode_access_token(token).get("sub")
    except:
        payload = None

    if payload:
        is_token_valid = True

    return is_token_valid

def get_current_user(
    token: Optional[HTTPAuthorizationCredentials] = Depends(JWTBearer()),
    db: Session  =  Depends(get_db)
) -> User:
    payload_data = decode_access_token(token)
    username =  payload_data.get('sub')
    user  = db.query(User).filter(User.username== username).first()
    if user:
        return user
    else :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    
