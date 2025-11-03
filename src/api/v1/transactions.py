from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.v1 import schemas, services, dependency_providers
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["transactions"])


@router.post(
    "/", response_model=schemas.TransactionRead, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    payload: schemas.TransactionCreate,
    db: AsyncSession = Depends(dependency_providers.get_db_session),
):
    try:
        tx = await services.create_transaction_service(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return tx


@router.get("/{transaction_id}", response_model=schemas.TransactionRead)
async def read_transaction(
    transaction_id: int, db: AsyncSession = Depends(dependency_providers.get_db_session)
):
    tx = await services.get_transaction_service(db, transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return tx


@router.get("/list", response_model=List[schemas.TransactionRead])
async def list_transactions(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(dependency_providers.get_db_session),
):
    return await services.list_transactions_service(db, limit=limit, offset=offset)


@router.patch("/{transaction_id}", response_model=schemas.TransactionRead)
async def patch_transaction(
    transaction_id: int,
    payload: schemas.TransactionUpdate,
    db: AsyncSession = Depends(dependency_providers.get_db_session),
):
    tx = await services.update_transaction_service(db, transaction_id, payload)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return tx


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_transaction(
    transaction_id: int, db: AsyncSession = Depends(dependency_providers.get_db_session)
):
    await services.delete_transaction_service(db, transaction_id)
    return None
