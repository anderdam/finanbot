from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.finanbot.models.orm_models import User
from src.finanbot.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token with provided payload.
    Caller should include 'sub' when appropriate.
    Uses UTC times for expiry.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expires_minutes)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_access_token_for_user(
    user_id: UUID,
    extra_claims: Optional[dict] = None,
    expires: Optional[timedelta] = None,
) -> str:
    """
    Convenience: creates a token with subject ('sub') set to the user id string.
    """
    payload = {"sub": str(user_id)}
    if extra_claims:
        payload.update(extra_claims)
    return create_access_token(payload, expires_delta=expires)


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str,
    db: Session,
) -> User:
    """
    Resolve the current user from the bearer token.
    Raises 401 on any validation error.
    """
    credentials_exception = _credentials_exception()

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as err:
        # Chain from the original JWTError so it's clear why validation failed
        raise credentials_exception from err

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError) as err:
        # Chain the parsing error to preserve original cause while raising a 401
        raise credentials_exception from err

    user = db.get(User, user_uuid)
    if user is None:
        raise credentials_exception

    return user
