from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..models import PhoneNumber, PhoneReport

HIGH_RISK_CATEGORIES = {"trata_personas", "sim_swapping", "extorsion", "secuestro_virtual"}
MEDIUM_RISK_CATEGORIES = {"estafa", "phishing", "vishing", "suplantacion"}


@dataclass(slots=True)
class ScoringResult:
    score: int
    risk_level: str
    fraud_category: str
    total_reports: int
    recent_reports_7d: int
    simulated_call_volume: int
    number_age_days: int
    factors: list[str]


def _score_to_level(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def _dominant_category(reports: list[PhoneReport]) -> str:
    if not reports:
        return "unknown"
    counts: dict[str, int] = {}
    for r in reports:
        counts[r.category] = counts.get(r.category, 0) + 1
    return max(counts, key=counts.get)


def compute_risk_score(db: Session, phone: PhoneNumber) -> ScoringResult:
    now = datetime.now(timezone.utc)
    factors: list[str] = []
    score = 0

    reports = (
        db.query(PhoneReport)
        .filter(PhoneReport.phone_number_id == phone.id)
        .order_by(PhoneReport.created_at.desc())
        .all()
    )

    # --- Factor 1: Total report volume (max 30 pts) ---
    total = len(reports)
    if total >= 10:
        score += 30
        factors.append(f"{total} reportes totales: volumen critico")
    elif total >= 5:
        score += 20
        factors.append(f"{total} reportes totales: volumen alto")
    elif total >= 2:
        score += 10
        factors.append(f"{total} reportes totales")
    elif total == 1:
        score += 5
        factors.append("1 reporte registrado")

    # --- Factor 2: Recent reports in last 7 days (max 25 pts) ---
    cutoff_7d = now - timedelta(days=7)
    recent = [
        r for r in reports
        if r.created_at and r.created_at.replace(tzinfo=timezone.utc) >= cutoff_7d
    ]
    recent_count = len(recent)
    if recent_count >= 5:
        score += 25
        factors.append(f"{recent_count} reportes en ultimos 7 dias: patron activo")
    elif recent_count >= 3:
        score += 15
        factors.append(f"{recent_count} reportes recientes")
    elif recent_count >= 1:
        score += 8
        factors.append(f"{recent_count} reporte(s) reciente(s)")

    # --- Factor 3: Category severity (max 25 pts) ---
    category = _dominant_category(reports)
    has_high = any(r.category in HIGH_RISK_CATEGORIES for r in reports)
    has_medium = any(r.category in MEDIUM_RISK_CATEGORIES for r in reports)
    if has_high:
        score += 25
        high_cats = {r.category for r in reports if r.category in HIGH_RISK_CATEGORIES}
        factors.append(
            f"Categoria de alto riesgo: {', '.join(sorted(high_cats))}"
        )
    elif has_medium:
        score += 12
        factors.append(f"Categoria de riesgo medio: {category}")

    # --- Factor 4: Simulated call volume in 24h (max 10 pts) ---
    call_vol = phone.simulated_call_count_24h
    if call_vol >= 50:
        score += 10
        factors.append(f"{call_vol} llamadas simuladas en 24h: volumen anomalo")
    elif call_vol >= 20:
        score += 6
        factors.append(f"{call_vol} llamadas simuladas en 24h")

    # --- Factor 5: Number age (max 10 pts — newer = riskier) ---
    _created = phone.created_at.replace(tzinfo=timezone.utc) if phone.created_at else now
    age_days = max(0, (now - _created).days)
    if age_days <= 7:
        score += 10
        factors.append(f"Numero registrado hace {age_days} dias: muy reciente")
    elif age_days <= 30:
        score += 6
        factors.append(f"Numero registrado hace {age_days} dias: reciente")
    elif age_days <= 90:
        score += 3
        factors.append(f"Numero con {age_days} dias de antiguedad")

    score = min(100, score)

    return ScoringResult(
        score=score,
        risk_level=_score_to_level(score),
        fraud_category=category,
        total_reports=total,
        recent_reports_7d=recent_count,
        simulated_call_volume=call_vol,
        number_age_days=age_days,
        factors=factors,
    )
