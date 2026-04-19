from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.account import AccountFollowUpResponse, AccountReportedUpdateRequest
from ..services.follow_up_service import get_account_follow_up, set_account_reported

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.get("/{account_number}/follow-up", response_model=AccountFollowUpResponse)
def follow_up(
    account_number: str,
    db: Session = Depends(get_db),
):
    return get_account_follow_up(db, account_number)


@router.patch("/{account_number}/reported", response_model=AccountFollowUpResponse)
def update_reported_status(
    account_number: str,
    payload: AccountReportedUpdateRequest,
    db: Session = Depends(get_db),
):
    return set_account_reported(
        db,
        account_number,
        reported=payload.reported,
    )
