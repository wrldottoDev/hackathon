from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import require_service_token
from ..database import get_db
from ..schemas.transaction import (
    InterbankReceiveRequest,
    InterbankReversalRequest,
    TransactionResponse,
)
from ..services.transaction_service import (
    receive_interbank_transfer,
    reverse_interbank_transfer,
)

router = APIRouter(prefix="/interbank", tags=["interbank"])


@router.post(
    "/receive",
    response_model=TransactionResponse,
    status_code=201,
    dependencies=[Depends(require_service_token)],
)
def receive_transfer(
    data: InterbankReceiveRequest,
    db: Session = Depends(get_db),
):
    return receive_interbank_transfer(db, data)


@router.post(
    "/reverse",
    response_model=TransactionResponse,
    dependencies=[Depends(require_service_token)],
)
def reverse_transfer(
    data: InterbankReversalRequest,
    db: Session = Depends(get_db),
):
    return reverse_interbank_transfer(db, data)
