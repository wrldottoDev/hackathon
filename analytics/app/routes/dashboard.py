from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.dashboard import DashboardResponse
from ..services import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.get("/summary", response_model=DashboardResponse)
def dashboard_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard(db)
