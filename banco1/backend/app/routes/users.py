from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[schemas.UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user
    return crud.get_users(db)
