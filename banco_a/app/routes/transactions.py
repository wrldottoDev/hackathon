from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, require_service_token
from ..database import get_db
from ..models.user import User
from ..schemas.transaction import TransactionResponse, TransferRequest
from ..settings import TRANSACTION_EXPORT_LIMIT
from ..services.transaction_service import (
    create_internal_transfer,
    create_interbank_transfer,
    get_transactions_for_export,
    get_transactions_by_user,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/internal", response_model=TransactionResponse, status_code=201)
def internal_transfer(
    data: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_internal_transfer(db, data, current_user)


@router.post("/interbank", response_model=TransactionResponse, status_code=201)
def interbank_transfer(
    data: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_interbank_transfer(db, data, current_user)


@router.get("/my", response_model=list[TransactionResponse])
def my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transactions_by_user(db, current_user)


@router.get(
    "/export",
    response_model=list[TransactionResponse],
    dependencies=[Depends(require_service_token)],
)
def export_transactions(
    since: datetime | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=TRANSACTION_EXPORT_LIMIT),
    db: Session = Depends(get_db),
):
    return get_transactions_for_export(db, since=since, limit=limit)
