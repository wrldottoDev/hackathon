from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..models.finsta_alert import FinstaAlert

router = APIRouter(
    tags=["finsta"],
    dependencies=[Depends(require_analytics_api_key)],
)


class FinstaAlertPayload(BaseModel):
    source: str = "finsta"
    category: str
    pattern_type: str
    score: int
    level: str
    reason: str
    username: str
    target_type: str
    target_id: int
    rules_triggered: list[dict[str, Any]] = []
    created_at: datetime | None = None


class FinstaAlertResponse(BaseModel):
    id: int
    source: str
    category: str
    pattern_type: str
    score: int
    level: str
    reason: str
    username: str
    target_type: str
    target_id: int
    rules_triggered: list[dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/finsta-alerts", status_code=201)
def receive_finsta_alerts(
    alerts: list[FinstaAlertPayload],
    db: Session = Depends(get_db),
):
    created = []
    for payload in alerts:
        alert = FinstaAlert(
            source=payload.source,
            category=payload.category,
            pattern_type=payload.pattern_type,
            score=payload.score,
            level=payload.level,
            reason=payload.reason,
            username=payload.username,
            target_type=payload.target_type,
            target_id=payload.target_id,
            rules_triggered=payload.rules_triggered,
            created_at=payload.created_at or datetime.now(timezone.utc),
        )
        db.add(alert)
        created.append(alert)
    db.commit()
    return {"status": "ok", "received": len(created)}


@router.get("/finsta-alerts", response_model=list[FinstaAlertResponse])
def list_finsta_alerts(
    level: str | None = None,
    username: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(FinstaAlert).order_by(FinstaAlert.created_at.desc())
    if level:
        query = query.filter(FinstaAlert.level == level)
    if username:
        query = query.filter(FinstaAlert.username == username)
    return query.limit(limit).all()


@router.get("/finsta-alerts/summary")
def finsta_alerts_summary(db: Session = Depends(get_db)):
    alerts = db.query(FinstaAlert).all()
    by_level = {}
    by_user = {}
    for alert in alerts:
        by_level[alert.level] = by_level.get(alert.level, 0) + 1
        by_user[alert.username] = by_user.get(alert.username, 0) + 1
    return {
        "total": len(alerts),
        "by_level": by_level,
        "by_user": dict(sorted(by_user.items(), key=lambda x: x[1], reverse=True)),
    }
