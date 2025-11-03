from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

from src.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# JWT helpers
def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expires = datetime.utcnow() + timedelta(
        minutes=(expires_minutes or settings.access_token_expires_minutes)
    )
    payload = {"sub": str(subject), "exp": expires}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
