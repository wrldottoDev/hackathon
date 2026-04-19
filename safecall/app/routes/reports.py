from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..core.phone_numbers import normalize_cr_phone_number, pick_service_provider
from ..database import get_db
from ..models import PhoneNumber, PhoneReport, User
from ..schemas import ReportCreate, ReportOut
from ..services.analytics_bridge import forward_phone_alert
from ..services.scoring import HIGH_RISK_CATEGORIES, compute_risk_score

router = APIRouter(prefix="/api", tags=["reports"])


def _hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return hashlib.sha256(ip.encode()).hexdigest()

@router.post("/report", response_model=ReportOut, status_code=201)
async def create_report(
    payload: ReportCreate,
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    reporter = db.query(User).filter(User.id == payload.reporter_id).first()
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter no encontrado")

    normalized = normalize_cr_phone_number(payload.reported_number)

    phone = db.query(PhoneNumber).filter(PhoneNumber.number == normalized).first()
    if not phone:
        phone = PhoneNumber(number=normalized, carrier=pick_service_provider(normalized))
        db.add(phone)
        db.flush()
    else:
        phone.carrier = pick_service_provider(normalized)

    report = PhoneReport(
        reporter_id=payload.reporter_id,
        phone_number_id=phone.id,
        reported_number=normalized,
        category=payload.category,
        description=payload.description,
        evidence_hash=payload.evidence_hash,
        consent_data_processing=payload.consent_data_processing,
        reporter_ip_hash=_hash_ip(request.client.host if request.client else None),
    )

    db.add(report)
    db.flush()

    scoring = compute_risk_score(db, phone)
    report.risk_level = scoring.risk_level

    phone.total_reports = scoring.total_reports
    phone.last_reported_at = datetime.now(timezone.utc)

    if scoring.score >= 80:
        phone.is_blocked = True

    db.commit()
    db.refresh(report)

    if payload.category in HIGH_RISK_CATEGORIES or scoring.score >= 60:
        report.forwarded_to_analytics = True
        db.commit()
        background.add_task(
            forward_phone_alert,
            {
                "source": "safecall",
                "number": normalized,
                "carrier": phone.carrier,
                "category": payload.category,
                "risk_score": scoring.score,
                "risk_level": scoring.risk_level,
                "total_reports": scoring.total_reports,
                "factors": scoring.factors,
            },
        )

    return report


@router.get("/reports", response_model=list[ReportOut])
def list_reports(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return (
        db.query(PhoneReport)
        .order_by(PhoneReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
