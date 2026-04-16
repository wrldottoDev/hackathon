from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return crud.create_transaction(db, tx, actor=current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/my", response_model=list[schemas.TransactionResponse])
def list_my_transactions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud.get_transactions_by_user(db, current_user.id)


@router.get("", response_model=list[schemas.TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user
    return crud.get_transactions(db)


@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user
    transaction = crud.get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaction
