from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.bank import BankRegistryCreate, BankRegistryResponse
from ..services.bank_service import list_banks, upsert_bank

router = APIRouter(
    prefix="/banks",
    tags=["banks"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.post("/register", response_model=BankRegistryResponse, status_code=201)
def register_bank(
    data: BankRegistryCreate,
    db: Session = Depends(get_db),
):
    return upsert_bank(db, data)


@router.get("", response_model=list[BankRegistryResponse])
def get_banks(db: Session = Depends(get_db)):
    return list_banks(db)

