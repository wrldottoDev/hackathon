from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.transaction import FetchTransactionsResponse
from ..services.fetch_service import fetch_transactions_from_registered_banks

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.get("/fetch", response_model=FetchTransactionsResponse)
def fetch_transactions(db: Session = Depends(get_db)):
    return fetch_transactions_from_registered_banks(db)

