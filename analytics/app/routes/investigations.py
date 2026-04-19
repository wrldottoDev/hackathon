from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.investigation import (
    InvestigationCreate,
    InvestigationResponse,
    InvestigationSummaryResponse,
    InvestigationUpdate,
)
from ..services import investigation_service

router = APIRouter(
    prefix="/investigations",
    tags=["investigations"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.post("", response_model=InvestigationResponse, status_code=201)
def create_investigation(
    data: InvestigationCreate,
    db: Session = Depends(get_db),
):
    return investigation_service.create_investigation(db, data)


@router.get("", response_model=list[InvestigationResponse])
def list_investigations(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return investigation_service.list_investigations(
        db, status=status, priority=priority, category=category, limit=limit,
    )


@router.get("/summary", response_model=InvestigationSummaryResponse)
def investigation_summary(db: Session = Depends(get_db)):
    return investigation_service.get_investigation_summary(db)


@router.get("/{case_number}", response_model=InvestigationResponse)
def get_investigation(case_number: str, db: Session = Depends(get_db)):
    result = investigation_service.get_investigation(db, case_number)
    if result is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return result


@router.patch("/{case_number}", response_model=InvestigationResponse)
def update_investigation(
    case_number: str,
    data: InvestigationUpdate,
    db: Session = Depends(get_db),
):
    result = investigation_service.update_investigation(db, case_number, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return result
