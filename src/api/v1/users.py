from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1 import schemas
from src.api.v1.dependency_providers import (
    get_db_session,
    get_current_user,
    require_admin,
)
from src.api.v1 import services
from src.core.config import get_settings
from src.core.security import create_access_token
from src.models.orm_models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED
)
async def register(
    payload: schemas.UserCreate, db: AsyncSession = Depends(get_db_session)
):
    try:
        user = await services.register_user(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    user_id = await services.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(subject=str(user_id))
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": get_settings().access_token_expires_minutes * 60,
    }


@router.get("/me", response_model=schemas.UserRead)
async def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=schemas.UserRead)
async def update_me(
    payload: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    user = await services.update_user_service(db, current_user.id, payload)
    return user


# Admin endpoints
@router.get(
    "/", response_model=list[schemas.UserRead], dependencies=[Depends(require_admin)]
)
async def list_users(db: AsyncSession = Depends(get_db_session)):
    # light-weight list; production: use pagination
    q = await db.execute(select(User).order_by(User.created_at.desc()))
    return q.scalars().all()
