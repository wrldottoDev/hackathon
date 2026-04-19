from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, require_service_token
from ..database import get_db
from ..models.user import User
from ..schemas.account import AccountCreate, AccountResponse, SimulatePinChangeRequest
from ..services.account_service import (
    create_account,
    get_account_by_id,
    get_accounts_for_export,
    get_accounts_by_user,
    mark_simulated_pin_change,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountResponse, status_code=201)
def create(
    data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_account(
        db,
        current_user,
        data.initial_balance,
        current_location=data.current_location,
    )


@router.get(
    "/export",
    response_model=list[AccountResponse],
    dependencies=[Depends(require_service_token)],
)
def export_accounts(db: Session = Depends(get_db)):
    return get_accounts_for_export(db)


@router.get("/my", response_model=list[AccountResponse])
def my_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_accounts_by_user(db, current_user)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_account_by_id(db, account_id, current_user)


@router.post("/{account_id}/simulate-pin-change", response_model=AccountResponse)
def simulate_pin_change(
    account_id: int,
    data: SimulatePinChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mark_simulated_pin_change(
        db,
        account_id,
        current_user,
        location=data.location,
    )
