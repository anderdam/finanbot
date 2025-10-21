from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.finanbot.models.orm_models import User
from src.finanbot.core.config import get_settings
from src.finanbot.db.session import get_db

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
depended_db = Depends(get_db)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = depended_db,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise credentials_exception
        try:
            user_uuid = UUID(user_id)
        except (ValueError, TypeError) as err:
            raise credentials_exception from err

    except JWTError as err:
        raise credentials_exception from err

    user = db.get(User, user_uuid)
    if user is None:
        raise credentials_exception
    return user
