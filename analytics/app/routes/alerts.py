from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.alert import RiskAlertResponse, RiskAlertSummaryResponse
from ..services.risk_service import get_alert_summary, list_alerts

router = APIRouter(
    tags=["alerts"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.get("/alerts", response_model=list[RiskAlertResponse])
def get_alerts(
    bank_code: str | None = Query(default=None),
    account_number: str | None = Query(default=None),
    level: str | None = Query(default=None),
    category: str | None = Query(default=None),
    pattern_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_alerts(
        db,
        bank_code=bank_code,
        account_number=account_number,
        level=level,
        category=category,
        pattern_type=pattern_type,
        limit=limit,
    )


@router.get("/alerts/summary", response_model=RiskAlertSummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    return get_alert_summary(db)
