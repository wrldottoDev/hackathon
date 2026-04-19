from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..services.report_service import build_account_report_pdf

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.get("/accounts/{account_number}/pdf")
def account_report(
    account_number: str,
    db: Session = Depends(get_db),
):
    try:
        payload = build_account_report_pdf(db, account_number)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    filename = f"flowlens-report-{account_number.strip().upper()}.pdf"
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )
