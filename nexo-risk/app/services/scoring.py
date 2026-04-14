"""
Motor de scoring de NEXO Risk
=============================
Evalúa una cuenta y sus transacciones contra 5 señales de riesgo.
Cada señal es explicable, parametrizable y justificable ante el jurado.

Señales:
  S1 - Múltiples depósitos pequeños     (peso 30)
  S2 - Remitentes múltiples             (peso 25)
  S3 - Dispersión rápida de fondos      (peso 20)
  S4 - Actividad nocturna               (peso 15)
  S5 - Reincidencia relacional          (peso 10)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.models.db import Account, Transaction


# ── Parámetros por defecto (parametrizables) ──────────────────────────────────

PARAMS = {
    "S1_min_deposits":     5,        # cantidad mínima de depósitos pequeños
    "S1_small_threshold":  500.0,    # monto máximo considerado "pequeño"
    "S1_window_hours":     24,       # ventana de tiempo en horas
    "S2_min_senders":      4,        # remitentes distintos mínimo
    "S2_window_days":      7,
    "S3_ratio_threshold":  0.7,      # fracción del saldo saliente en ventana
    "S3_window_hours":     48,
    "S4_night_start":      22,       # hora de inicio (22:00)
    "S4_night_end":        6,        # hora de fin (06:00)
    "S4_min_night_ratio":  0.35,     # fracción mínima de txns nocturnas
    "S5_min_recurrence":   3,        # cuántas veces debe reaparecer una cuenta
}

WEIGHTS = {"S1": 30, "S2": 25, "S3": 20, "S4": 15, "S5": 10}


# ── Resultado de una señal ─────────────────────────────────────────────────────

@dataclass
class SignalResult:
    code:        str
    triggered:   bool
    weight:      int
    score_added: float          # 0..weight
    label:       str
    detail:      str


@dataclass
class ScoringResult:
    account_id:     str
    account_code:   str
    score:          float               # 0..100
    risk_level:     str                 # low / medium / high / escalate
    signals:        List[SignalResult] = field(default_factory=list)
    summary:        str = ""
    recommendation: str = ""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _is_night(ts: datetime, start: int, end: int) -> bool:
    h = ts.hour
    if start > end:          # cruza medianoche: ej. 22–06
        return h >= start or h < end
    return start <= h < end


def _risk_level(score: float) -> str:
    if score >= 75:
        return "escalate"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def _recommendation(level: str) -> str:
    return {
        "escalate": "Escalar de inmediato a oficial de cumplimiento senior.",
        "high":     "Revisar manualmente en las próximas 24 horas.",
        "medium":   "Monitorear durante los próximos 7 días.",
        "low":      "Sin acción requerida. Registrar y archivar.",
    }[level]


def _summary(signals: List[SignalResult], score: float, level: str) -> str:
    triggered = [s for s in signals if s.triggered]
    if not triggered:
        return "No se detectaron señales de riesgo relevantes en esta cuenta."
    names = ", ".join(s.label for s in triggered)
    return (
        f"Se detectaron {len(triggered)} señal(es) de riesgo: {names}. "
        f"Score total: {score:.1f}/100. Nivel: {level.upper()}. "
        f"Se recomienda {_recommendation(level).lower()}"
    )


# ── Señales ────────────────────────────────────────────────────────────────────

def signal_s1(received: List[Transaction], p: dict) -> SignalResult:
    """Múltiples depósitos pequeños en ventana corta."""
    now = max((t.timestamp for t in received), default=datetime.utcnow())
    cutoff = now - timedelta(hours=p["S1_window_hours"])
    small = [
        t for t in received
        if t.amount <= p["S1_small_threshold"] and t.timestamp >= cutoff
    ]
    triggered = len(small) >= p["S1_min_deposits"]
    score_added = WEIGHTS["S1"] if triggered else 0.0
    return SignalResult(
        code="S1",
        triggered=triggered,
        weight=WEIGHTS["S1"],
        score_added=score_added,
        label="Depósitos pequeños múltiples",
        detail=(
            f"{len(small)} depósito(s) ≤ ${p['S1_small_threshold']:.0f} "
            f"en las últimas {p['S1_window_hours']}h "
            f"(umbral: {p['S1_min_deposits']})"
        ),
    )


def signal_s2(received: List[Transaction], p: dict) -> SignalResult:
    """Remitentes múltiples sin relación aparente."""
    now = max((t.timestamp for t in received), default=datetime.utcnow())
    cutoff = now - timedelta(days=p["S2_window_days"])
    senders = {t.sender_id for t in received if t.timestamp >= cutoff}
    triggered = len(senders) >= p["S2_min_senders"]
    score_added = WEIGHTS["S2"] if triggered else 0.0
    return SignalResult(
        code="S2",
        triggered=triggered,
        weight=WEIGHTS["S2"],
        score_added=score_added,
        label="Remitentes múltiples",
        detail=(
            f"{len(senders)} remitente(s) distinto(s) en los últimos "
            f"{p['S2_window_days']} día(s) (umbral: {p['S2_min_senders']})"
        ),
    )


def signal_s3(
    received: List[Transaction],
    sent: List[Transaction],
    p: dict,
) -> SignalResult:
    """Dispersión rápida: entra dinero y sale rápido."""
    if not received:
        return SignalResult("S3", False, WEIGHTS["S3"], 0.0,
                            "Dispersión rápida", "Sin ingresos para evaluar.")

    now = max((t.timestamp for t in received), default=datetime.utcnow())
    cutoff = now - timedelta(hours=p["S3_window_hours"])

    inflow  = sum(t.amount for t in received if t.timestamp >= cutoff)
    outflow = sum(t.amount for t in sent     if t.timestamp >= cutoff)

    ratio = outflow / inflow if inflow > 0 else 0.0
    triggered = ratio >= p["S3_ratio_threshold"] and inflow > 0
    score_added = WEIGHTS["S3"] if triggered else 0.0
    return SignalResult(
        code="S3",
        triggered=triggered,
        weight=WEIGHTS["S3"],
        score_added=score_added,
        label="Dispersión rápida de fondos",
        detail=(
            f"Ingresó ${inflow:.2f} y salió ${outflow:.2f} "
            f"({ratio*100:.0f}%) en {p['S3_window_hours']}h "
            f"(umbral: {p['S3_ratio_threshold']*100:.0f}%)"
        ),
    )


def signal_s4(all_txns: List[Transaction], p: dict) -> SignalResult:
    """Actividad nocturna inusual."""
    if not all_txns:
        return SignalResult("S4", False, WEIGHTS["S4"], 0.0,
                            "Actividad nocturna", "Sin transacciones.")
    night = sum(1 for t in all_txns if _is_night(t.timestamp, p["S4_night_start"], p["S4_night_end"]))
    ratio = night / len(all_txns)
    triggered = ratio >= p["S4_min_night_ratio"]
    score_added = WEIGHTS["S4"] if triggered else 0.0
    return SignalResult(
        code="S4",
        triggered=triggered,
        weight=WEIGHTS["S4"],
        score_added=score_added,
        label="Actividad nocturna",
        detail=(
            f"{night}/{len(all_txns)} transacciones fuera de horario "
            f"({ratio*100:.0f}%) (umbral: {p['S4_min_night_ratio']*100:.0f}%)"
        ),
    )


def signal_s5(
    received: List[Transaction],
    sent: List[Transaction],
    account_id: str,
    db: Session,
    p: dict,
) -> SignalResult:
    """Reincidencia relacional: cuentas que reaparecen en múltiples casos."""
    from app.models.db import Case  # evitar import circular

    # Cuentas que interactúan con esta cuenta
    related_ids = {t.sender_id for t in received} | {t.receiver_id for t in sent}
    related_ids.discard(account_id)

    # Contar en cuántos casos activos aparece cada cuenta relacionada
    recurrent = 0
    for rid in related_ids:
        existing = (
            db.query(Case)
            .filter(Case.account_id == rid, Case.status != "dismissed")
            .count()
        )
        if existing >= 1:
            recurrent += 1

    triggered = recurrent >= p["S5_min_recurrence"]
    score_added = WEIGHTS["S5"] if triggered else 0.0
    return SignalResult(
        code="S5",
        triggered=triggered,
        weight=WEIGHTS["S5"],
        score_added=score_added,
        label="Reincidencia relacional",
        detail=(
            f"{recurrent} cuenta(s) relacionada(s) con casos previos "
            f"(umbral: {p['S5_min_recurrence']})"
        ),
    )


# ── Función principal ──────────────────────────────────────────────────────────

def score_account(account: Account, db: Session, params: dict | None = None) -> ScoringResult:
    """
    Evalúa una cuenta y devuelve su ScoringResult completo.
    """
    p = {**PARAMS, **(params or {})}

    received = list(account.transactions_received)
    sent     = list(account.transactions_sent)
    all_txns = received + sent

    signals = [
        signal_s1(received, p),
        signal_s2(received, p),
        signal_s3(received, sent, p),
        signal_s4(all_txns, p),
        signal_s5(received, sent, account.id, db, p),
    ]

    score = sum(s.score_added for s in signals)
    level = _risk_level(score)
    summary = _summary(signals, score, level)
    recommendation = _recommendation(level)

    return ScoringResult(
        account_id=account.id,
        account_code=account.code,
        score=score,
        risk_level=level,
        signals=signals,
        summary=summary,
        recommendation=recommendation,
    )
