from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.report import Report
from ..schemas.report import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=201)
def create_report(
    reporter_id: int = Query(...),
    payload: ReportCreate = ...,
    db: Session = Depends(get_db),
):
    if not payload.reported_user_id and not payload.post_id and not payload.message_id:
        raise HTTPException(400, "Must report a user, post, or message")
    report = Report(reporter_id=reporter_id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportResponse.model_validate(report)


@router.get("", response_model=list[ReportResponse])
def list_reports(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Report).order_by(Report.created_at.desc())
    if status:
        query = query.filter(Report.status == status)
    return [ReportResponse.model_validate(r) for r in query.limit(limit).all()]


@router.patch("/{report_id}/resolve")
def resolve_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    report.status = "resolved"
    db.commit()
    return {"detail": "Report resolved"}
