from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.resolved_case import CorrelationRunRequest, ResolvedCaseResponse
from ..services.intelligence_engine import (
    GeminiCorrelationFailure,
    InsufficientCorrelationData,
    IntelligenceEngine,
    IntelligenceEngineUnavailable,
)

router = APIRouter(
    prefix="/cases",
    tags=["resolved-cases"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.post("/resolved", response_model=ResolvedCaseResponse, status_code=status.HTTP_201_CREATED)
def run_resolved_case(
    request: CorrelationRunRequest,
    db: Session = Depends(get_db),
):
    try:
        case = IntelligenceEngine().correlate_recent_activity(
            db,
            lookback_hours=request.lookback_hours,
            alert_limit=request.alert_limit,
            transaction_limit=request.transaction_limit,
        )
    except InsufficientCorrelationData as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except IntelligenceEngineUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El motor de correlacion no esta disponible.",
        ) from exc
    except GeminiCorrelationFailure as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El analisis externo no pudo completarse.",
        ) from exc

    return _to_response(case)


@router.get("/resolved", response_model=list[ResolvedCaseResponse])
def list_resolved_cases(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    cases = IntelligenceEngine().list_cases(db, limit=limit)
    return [_to_response(case) for case in cases]


@router.get("/resolved/{case_id}", response_model=ResolvedCaseResponse)
def get_resolved_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    case = IntelligenceEngine().get_case(db, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso resuelto no encontrado.",
        )
    return _to_response(case)


def _to_response(case) -> ResolvedCaseResponse:
    return ResolvedCaseResponse(
        id=case.id,
        created_at=case.created_at,
        period_start=case.period_start,
        period_end=case.period_end,
        score_de_vinculacion=case.score_de_vinculacion,
        justificacion_tecnica=case.justificacion_tecnica,
        hallazgos_json=dict(case.hallazgos_json or {}),
        alert_ids=list(case.alert_ids or []),
        transaction_ids=list(case.transaction_ids or []),
        gemini_model=case.gemini_model,
    )
