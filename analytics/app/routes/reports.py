from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.infrastructure import EvidenceDossierResponse
from ..services.report_service import (
    build_account_report_pdf,
    build_evidence_dossier_json,
    build_evidence_dossier_pdf,
)

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


@router.get("/cases/{case_id}/evidence.json", response_model=EvidenceDossierResponse)
def case_evidence_json(
    case_id: int,
    db: Session = Depends(get_db),
):
    try:
        return build_evidence_dossier_json(db, case_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/cases/{case_id}/evidence.pdf")
def case_evidence_pdf(
    case_id: int,
    db: Session = Depends(get_db),
):
    try:
        payload = build_evidence_dossier_pdf(db, case_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    filename = f"flowlens-expediente-{case_id}.pdf"
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )
