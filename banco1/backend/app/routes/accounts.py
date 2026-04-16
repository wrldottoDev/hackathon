from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=schemas.AccountResponse)
def create_account(
    account: schemas.AccountCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud.create_account(db, current_user, initial_balance=account.initial_balance)


@router.get("/my", response_model=list[schemas.AccountResponse])
def list_my_accounts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud.get_accounts_by_user(db, current_user.id)


@router.get("", response_model=list[schemas.AccountResponse])
def list_accounts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user
    return crud.get_accounts(db)


@router.get("/{account_id}", response_model=schemas.AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user
    account = crud.get_account_by_id(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return account
