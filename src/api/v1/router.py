from fastapi import APIRouter
from .transactions import router as transactions_router
from .attachments import router as attachments_router
from .users import router as users_router

router = APIRouter(prefix="/v1", tags=["api_v1_router"])
router.include_router(
    transactions_router, prefix="/transactions", tags=["transactions"]
)
router.include_router(attachments_router, prefix="/attachments", tags=["attachments"])
router.include_router(users_router, prefix="/users", tags=["users"])
