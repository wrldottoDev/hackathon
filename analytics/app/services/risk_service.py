from __future__ import annotations

from collections import Counter
from datetime import timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from ..core.money import sum_money
from ..models.observed_transaction import ObservedTransaction
from ..models.risk_alert import RiskAlert
from ..schemas.alert import RiskAlertResponse, RiskAlertSummaryResponse

HIGH_AMOUNT_THRESHOLD = Decimal("10000.00")
SMALL_TX_THRESHOLD = Decimal("250.00")
SMALL_TX_COUNT_THRESHOLD = 5
REPEATED_PAIR_THRESHOLD = 3
STAR_THRESHOLD = 4
RAPID_FLOW_RATIO = Decimal("0.70")


def _score_to_level(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 70:
        return "medium"
    return "high"


def _create_alert(
    db: Session,
    transaction: ObservedTransaction,
    *,
    account_number: str,
    bank_code: str,
    score: int,
    reason: str,
    pattern_type: str,
) -> None:
    db.add(
        RiskAlert(
            observed_transaction_id=transaction.id,
            transaction_id=transaction.external_transaction_id,
            account_number=account_number,
            bank_code=bank_code,
            score=score,
            level=_score_to_level(score),
            reason=reason,
            pattern_type=pattern_type,
        )
    )


def recompute_risk_alerts(db: Session) -> int:
    db.query(RiskAlert).delete()

    transactions = (
        db.query(ObservedTransaction)
        .filter(ObservedTransaction.status == "completed")
        .order_by(ObservedTransaction.created_at.asc(), ObservedTransaction.id.asc())
        .all()
    )

    for index, transaction in enumerate(transactions):
        prior_transactions = transactions[: index + 1]
        one_hour_ago = transaction.created_at - timedelta(hours=1)
        two_hours_ago = transaction.created_at - timedelta(hours=2)
        one_day_ago = transaction.created_at - timedelta(days=1)

        if transaction.amount >= HIGH_AMOUNT_THRESHOLD:
            _create_alert(
                db,
                transaction,
                account_number=transaction.source_account_number,
                bank_code=transaction.source_bank_code,
                score=80,
                reason=f"Monto alto sobre el umbral fijo de {HIGH_AMOUNT_THRESHOLD:,.0f}.",
                pattern_type="high_amount",
            )

        small_transactions = [
            item
            for item in prior_transactions
            if item.source_account_number == transaction.source_account_number
            and item.amount <= SMALL_TX_THRESHOLD
            and item.created_at >= one_hour_ago
        ]
        if (
            transaction.amount <= SMALL_TX_THRESHOLD
            and len(small_transactions) >= SMALL_TX_COUNT_THRESHOLD
        ):
            _create_alert(
                db,
                transaction,
                account_number=transaction.source_account_number,
                bank_code=transaction.source_bank_code,
                score=55,
                reason="Varias transacciones pequeñas en una ventana corta de tiempo.",
                pattern_type="burst_small_transactions",
            )

        repeated_pairs = [
            item
            for item in prior_transactions
            if item.source_account_number == transaction.source_account_number
            and item.destination_account_number == transaction.destination_account_number
            and item.created_at >= one_day_ago
        ]
        if len(repeated_pairs) >= REPEATED_PAIR_THRESHOLD:
            _create_alert(
                db,
                transaction,
                account_number=transaction.source_account_number,
                bank_code=transaction.source_bank_code,
                score=40,
                reason="Transferencias repetidas al mismo destino dentro de 24 horas.",
                pattern_type="repeated_destination",
            )

        recent_incoming = [
            item
            for item in prior_transactions
            if item.destination_account_number == transaction.source_account_number
            and item.created_at >= two_hours_ago
        ]
        incoming_total = sum_money(item.amount for item in recent_incoming)
        if incoming_total and transaction.amount >= incoming_total * RAPID_FLOW_RATIO:
            _create_alert(
                db,
                transaction,
                account_number=transaction.source_account_number,
                bank_code=transaction.source_bank_code,
                score=75,
                reason="Entrada y salida rápida de fondos desde la misma cuenta.",
                pattern_type="rapid_in_out",
            )

        star_senders = {
            item.source_account_number
            for item in prior_transactions
            if item.destination_account_number == transaction.destination_account_number
            and item.created_at >= one_day_ago
        }
        if len(star_senders) >= STAR_THRESHOLD:
            _create_alert(
                db,
                transaction,
                account_number=transaction.destination_account_number,
                bank_code=transaction.destination_bank_code,
                score=65,
                reason="Concentración tipo estrella hacia la misma cuenta destino.",
                pattern_type="star_concentration",
            )

        chain_origins = [
            item
            for item in prior_transactions
            if item.destination_account_number == transaction.source_account_number
            and item.created_at >= one_hour_ago
            and item.id != transaction.id
            and transaction.amount >= item.amount * RAPID_FLOW_RATIO
        ]
        if chain_origins:
            _create_alert(
                db,
                transaction,
                account_number=transaction.source_account_number,
                bank_code=transaction.source_bank_code,
                score=85,
                reason="Cadena rápida de transferencias entre múltiples cuentas.",
                pattern_type="rapid_chain",
            )

    db.commit()
    return db.query(RiskAlert).count()


def list_alerts(
    db: Session,
    *,
    bank_code: str | None = None,
    account_number: str | None = None,
    level: str | None = None,
    pattern_type: str | None = None,
    limit: int = 100,
) -> list[RiskAlertResponse]:
    query = db.query(RiskAlert).order_by(RiskAlert.created_at.desc(), RiskAlert.id.desc())
    if bank_code:
        query = query.filter(RiskAlert.bank_code == bank_code.upper())
    if account_number:
        query = query.filter(RiskAlert.account_number == account_number.upper())
    if level:
        query = query.filter(RiskAlert.level == level)
    if pattern_type:
        query = query.filter(RiskAlert.pattern_type == pattern_type)

    return [
        RiskAlertResponse(
            id=alert.id,
            transaction_id=alert.transaction_id,
            account_number=alert.account_number,
            bank_code=alert.bank_code,
            score=alert.score,
            level=alert.level,
            reason=alert.reason,
            pattern_type=alert.pattern_type,
            created_at=alert.created_at,
        )
        for alert in query.limit(limit).all()
    ]


def get_alert_summary(db: Session) -> RiskAlertSummaryResponse:
    alerts = db.query(RiskAlert).all()
    by_level = Counter(alert.level for alert in alerts)
    by_pattern = Counter(alert.pattern_type for alert in alerts)
    return RiskAlertSummaryResponse(
        total_alerts=len(alerts),
        low=by_level.get("low", 0),
        medium=by_level.get("medium", 0),
        high=by_level.get("high", 0),
        by_pattern=dict(sorted(by_pattern.items())),
    )
