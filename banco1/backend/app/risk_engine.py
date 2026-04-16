from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from . import models


HIGH_AMOUNT_THRESHOLD = 10_000
SMALL_TX_THRESHOLD = 250
NEAR_THRESHOLD_FLOOR = 9_500


def _score_to_level(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 70:
        return "medium"
    return "high"


def evaluate_transaction_risk(db: Session, transaction: models.Transaction) -> models.RiskAlert | None:
    score = 0
    reasons: list[str] = []
    now = transaction.created_at or datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)
    two_hours_ago = now - timedelta(hours=2)

    if transaction.amount >= HIGH_AMOUNT_THRESHOLD:
        score += 50
        reasons.append(f"Monto alto sobre el umbral fijo de {HIGH_AMOUNT_THRESHOLD:,.0f}.")

    if NEAR_THRESHOLD_FLOOR <= transaction.amount < HIGH_AMOUNT_THRESHOLD:
        score += 20
        reasons.append("Monto inusualmente cercano al umbral sospechoso.")

    recent_small_count = (
        db.query(models.Transaction)
        .filter(models.Transaction.source_account_id == transaction.source_account_id)
        .filter(models.Transaction.created_at >= one_hour_ago)
        .filter(models.Transaction.amount <= SMALL_TX_THRESHOLD)
        .count()
    )
    if transaction.amount <= SMALL_TX_THRESHOLD and recent_small_count >= 4:
        score += 25
        reasons.append("Varias transacciones pequeñas en poco tiempo desde la misma cuenta.")

    repeated_pair_count = (
        db.query(models.Transaction)
        .filter(models.Transaction.source_account_id == transaction.source_account_id)
        .filter(models.Transaction.destination_account_id == transaction.destination_account_id)
        .filter(models.Transaction.created_at >= one_day_ago)
        .count()
    )
    if repeated_pair_count >= 3:
        score += 15
        reasons.append("Transferencias repetidas al mismo destino en 24 horas.")

    recent_incoming = (
        db.query(models.Transaction)
        .filter(models.Transaction.destination_account_id == transaction.source_account_id)
        .filter(models.Transaction.created_at >= two_hours_ago)
        .all()
    )
    incoming_total = sum(item.amount for item in recent_incoming)
    if incoming_total and transaction.amount >= incoming_total * 0.7:
        score += 30
        reasons.append("Entrada y salida rápida de fondos en la misma cuenta.")

    score = min(score, 100)
    if score == 0:
        return None

    alert = models.RiskAlert(
        transaction_id=transaction.id,
        account_id=transaction.source_account_id,
        score=score,
        level=_score_to_level(score),
        reason=" ".join(reasons),
    )
    db.add(alert)
    db.flush()
    return alert
