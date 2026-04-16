from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/network", tags=["Network"])


@router.get("/graph", response_model=schemas.GraphResponse)
def graph(
    risk: Literal["all", "low", "medium", "high"] = Query(default="all"),
    user_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user
    try:
        return crud.get_network_graph(db, risk_level=risk, user_id=user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/report", response_model=schemas.NetworkReportResponse)
def report(
    user_id: int = Query(...),
    risk: Literal["all", "low", "medium", "high"] = Query(default="all"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    del current_user
    try:
        return crud.get_network_report(db, user_id=user_id, risk_level=risk)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
