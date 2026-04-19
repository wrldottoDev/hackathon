from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.investigation import Investigation
from ..models.risk_alert import RiskAlert
from ..schemas.investigation import (
    InvestigationCreate,
    InvestigationResponse,
    InvestigationSummaryResponse,
    InvestigationUpdate,
)


def _generate_case_number() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_id = uuid.uuid4().hex[:6].upper()
    return f"FL-{ts}-{short_id}"


def _score_to_priority(score: int) -> str:
    if score <= 25:
        return "low"
    if score <= 50:
        return "medium"
    if score <= 80:
        return "high"
    return "critical"


def create_investigation(
    db: Session,
    data: InvestigationCreate,
) -> InvestigationResponse:
    alerts = (
        db.query(RiskAlert)
        .filter(
            RiskAlert.account_number == data.account_number.upper(),
            RiskAlert.bank_code == data.bank_code.upper(),
        )
        .all()
    )
    max_score = max((a.score for a in alerts), default=0)
    pattern_types = sorted({a.pattern_type for a in alerts})

    investigation = Investigation(
        case_number=_generate_case_number(),
        account_number=data.account_number.upper(),
        bank_code=data.bank_code.upper(),
        category=data.category,
        status="open",
        priority=data.priority or _score_to_priority(max_score),
        assigned_to=data.assigned_to,
        notes=data.notes,
        risk_score=max_score,
        pattern_types=pattern_types,
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)
    return _to_response(investigation)


def update_investigation(
    db: Session,
    case_number: str,
    data: InvestigationUpdate,
) -> InvestigationResponse | None:
    investigation = (
        db.query(Investigation)
        .filter(Investigation.case_number == case_number.upper())
        .first()
    )
    if investigation is None:
        return None

    if data.status is not None:
        investigation.status = data.status
        if data.status == "closed":
            investigation.closed_at = datetime.now(timezone.utc)
    if data.priority is not None:
        investigation.priority = data.priority
    if data.assigned_to is not None:
        investigation.assigned_to = data.assigned_to
    if data.notes is not None:
        investigation.notes = data.notes
    investigation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(investigation)
    return _to_response(investigation)


def get_investigation(db: Session, case_number: str) -> InvestigationResponse | None:
    investigation = (
        db.query(Investigation)
        .filter(Investigation.case_number == case_number.upper())
        .first()
    )
    if investigation is None:
        return None
    return _to_response(investigation)


def list_investigations(
    db: Session,
    *,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    limit: int = 100,
) -> list[InvestigationResponse]:
    query = db.query(Investigation).order_by(
        Investigation.created_at.desc(),
        Investigation.id.desc(),
    )
    if status:
        query = query.filter(Investigation.status == status)
    if priority:
        query = query.filter(Investigation.priority == priority)
    if category:
        query = query.filter(Investigation.category == category)
    return [_to_response(inv) for inv in query.limit(limit).all()]


def get_investigation_summary(db: Session) -> InvestigationSummaryResponse:
    investigations = db.query(Investigation).all()
    by_status = Counter(inv.status for inv in investigations)
    by_category = Counter(inv.category for inv in investigations)
    by_priority = Counter(inv.priority for inv in investigations)
    return InvestigationSummaryResponse(
        total=len(investigations),
        open=by_status.get("open", 0),
        in_progress=by_status.get("in_progress", 0),
        escalated=by_status.get("escalated", 0),
        closed=by_status.get("closed", 0),
        by_category=dict(sorted(by_category.items())),
        by_priority=dict(sorted(by_priority.items())),
    )


def _to_response(inv: Investigation) -> InvestigationResponse:
    return InvestigationResponse(
        id=inv.id,
        case_number=inv.case_number,
        account_number=inv.account_number,
        bank_code=inv.bank_code,
        category=inv.category,
        status=inv.status,
        priority=inv.priority,
        assigned_to=inv.assigned_to,
        notes=inv.notes,
        risk_score=inv.risk_score,
        pattern_types=inv.pattern_types or [],
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        closed_at=inv.closed_at,
    )
