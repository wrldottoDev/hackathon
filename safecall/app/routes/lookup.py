from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.phone_numbers import normalize_cr_phone_number, pick_service_provider
from ..database import get_db
from ..models import PhoneNumber, PhoneReport
from ..schemas import LookupResponse, PhoneNumberSummary, ReportOut, ScoringOut
from ..services.scoring import compute_risk_score

router = APIRouter(prefix="/api", tags=["lookup"])


def _status_message(total_reports: int) -> str:
    if total_reports == 0:
        return "Todo esta bien. Este numero no tiene reportes registrados."
    if total_reports == 1:
        return "Hay 1 reporte registrado para este numero. Conviene revisar el detalle."
    return f"Hay {total_reports} reportes asociados a este numero. Revisa el nivel de riesgo."


@router.get("/lookup/{number}", response_model=LookupResponse)
def lookup_number(number: str, db: Session = Depends(get_db)):
    normalized = normalize_cr_phone_number(number)
    if not normalized:
        raise HTTPException(status_code=400, detail="Numero invalido")

    phone = db.query(PhoneNumber).filter(PhoneNumber.number == normalized).first()
    if not phone:
        phone = PhoneNumber(number=normalized, carrier=pick_service_provider(normalized))
        db.add(phone)
        db.commit()
        db.refresh(phone)

    expected_provider = pick_service_provider(phone.number)
    if phone.carrier != expected_provider:
        phone.carrier = expected_provider
        db.commit()
        db.refresh(phone)

    result = compute_risk_score(db, phone)

    recent = (
        db.query(PhoneReport)
        .filter(PhoneReport.phone_number_id == phone.id)
        .order_by(PhoneReport.created_at.desc())
        .limit(10)
        .all()
    )

    return LookupResponse(
        number=phone.number,
        carrier=phone.carrier,
        is_blocked=phone.is_blocked,
        status_message=_status_message(result.total_reports),
        scoring=ScoringOut(
            score=result.score,
            risk_level=result.risk_level,
            fraud_category=result.fraud_category,
            total_reports=result.total_reports,
            recent_reports_7d=result.recent_reports_7d,
            simulated_call_volume=result.simulated_call_volume,
            number_age_days=result.number_age_days,
            factors=result.factors,
        ),
        recent_reports=[ReportOut.model_validate(r) for r in recent],
    )


@router.get("/phone-numbers", response_model=list[PhoneNumberSummary])
def list_phone_numbers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    phones = (
        db.query(PhoneNumber)
        .order_by(PhoneNumber.total_reports.desc(), PhoneNumber.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    updated = False
    summaries: list[PhoneNumberSummary] = []
    for phone in phones:
        expected_provider = pick_service_provider(phone.number)
        if phone.carrier != expected_provider:
            phone.carrier = expected_provider
            updated = True

        scoring = compute_risk_score(db, phone)
        summaries.append(
            PhoneNumberSummary(
                number=phone.number,
                carrier=phone.carrier,
                total_reports=scoring.total_reports,
                is_blocked=phone.is_blocked,
                risk_level=scoring.risk_level,
                status_message=_status_message(scoring.total_reports),
            )
        )

    if updated:
        db.commit()

    return summaries
