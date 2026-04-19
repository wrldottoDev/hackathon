from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.external_alert import ExternalAlert
from ..settings import ANALYTICS_API_KEY

router = APIRouter(prefix="/api/external-intel", tags=["external-intel"])


class PhoneAlertPayload(BaseModel):
    source: str
    number: str
    carrier: str | None = None
    category: str
    risk_score: int
    risk_level: str
    total_reports: int = 0
    factors: list[str] = []


def _require_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != ANALYTICS_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


@router.post("/phone-alert", status_code=201)
def receive_phone_alert(
    payload: PhoneAlertPayload,
    db: Session = Depends(get_db),
    _key: str = Depends(_require_key),
):
    alert = ExternalAlert(
        alert_type=f"phone_{payload.category}",
        severity=payload.risk_level,
        description=(
            f"[SafeCall] Numero {payload.number} — {payload.category} "
            f"(proveedor: {payload.carrier or 'sin proveedor'}, "
            f"score {payload.risk_score}, {payload.total_reports} reportes). "
            f"Factores: {'; '.join(payload.factors[:5])}"
        ),
        source_service=payload.source,
        created_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"id": alert.id, "status": "registered"}


@router.get("/phone-alerts")
def list_phone_alerts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    alerts = (
        db.query(ExternalAlert)
        .filter(ExternalAlert.source_service == "safecall")
        .order_by(ExternalAlert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "description": a.description,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]
