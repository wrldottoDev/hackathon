from __future__ import annotations

import json
from collections import Counter
from datetime import datetime

from sqlalchemy.orm import Session

from ..core.money import ZERO_MONEY, to_money
from ..models.observed_account import ObservedAccount
from ..models.observed_transaction import ObservedTransaction
from ..models.risk_alert import RiskAlert
from ..schemas.alert import RiskAlertResponse, RiskAlertSummaryResponse
from .detection_engine import Cuenta, MotorDeteccion, ResultadoRegla, Transaccion
from .privacy_service import display_account_number


def _score_to_level(score: int) -> str:
    if score <= 25:
        return "low"
    if score <= 50:
        return "medium"
    if score <= 80:
        return "high"
    return "critical"


def _normalize_location_history(raw_value: object) -> list[str]:
    if isinstance(raw_value, list):
        return [
            str(item).strip()
            for item in raw_value
            if str(item).strip()
        ]
    if isinstance(raw_value, str) and raw_value.strip():
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            return [raw_value.strip()]
        if isinstance(parsed, list):
            return [
                str(item).strip()
                for item in parsed
                if str(item).strip()
            ]
    return []


def _domain_account_from_snapshot(snapshot: ObservedAccount) -> Cuenta:
    return Cuenta(
        numero_cuenta=snapshot.account_number,
        banco_codigo=snapshot.bank_code,
        estado=snapshot.status,
        saldo_actual=to_money(snapshot.balance),
        fecha_creacion=snapshot.created_at,
        fecha_ultima_actividad=snapshot.last_activity_at,
        fecha_ultimo_cambio_pin=snapshot.last_credentials_change_at,
        ubicacion_actual=snapshot.current_location or "",
        ubicaciones_historicas=_normalize_location_history(snapshot.location_history),
        reportada=bool(getattr(snapshot, "reported", False)),
        datos_protegidos_por_investigacion=bool(snapshot.data_protected_by_investigation),
    )


def _domain_account_from_transaction(
    account_number: str,
    bank_code: str,
    created_at: datetime,
    location: str,
) -> Cuenta:
    return Cuenta(
        numero_cuenta=account_number,
        banco_codigo=bank_code,
        estado="active",
        saldo_actual=ZERO_MONEY,
        fecha_creacion=created_at,
        fecha_ultima_actividad=created_at,
        fecha_ultimo_cambio_pin=None,
        ubicacion_actual=location or "",
        ubicaciones_historicas=[location] if location else [],
        reportada=False,
        datos_protegidos_por_investigacion=False,
    )


def _domain_transaction_from_observed(transaction: ObservedTransaction) -> Transaccion:
    return Transaccion(
        transaction_id=transaction.external_transaction_id,
        observed_transaction_id=transaction.id,
        cuenta_origen=transaction.source_account_number,
        cuenta_destino=transaction.destination_account_number,
        banco_origen=transaction.source_bank_code,
        banco_destino=transaction.destination_bank_code,
        monto=to_money(transaction.amount),
        fecha_hora=transaction.created_at,
        ubicacion_geografica=(transaction.location or "").strip(),
        beneficiario=(transaction.beneficiary or transaction.destination_account_number).strip(),
        concepto=(transaction.concept or transaction.description or "").strip(),
        canal=(transaction.channel or "").strip(),
        tipo=transaction.transaction_type,
        estado=transaction.status,
        saldo_origen_antes=to_money(transaction.source_balance_before)
        if transaction.source_balance_before is not None
        else None,
        saldo_origen_despues=to_money(transaction.source_balance_after)
        if transaction.source_balance_after is not None
        else None,
    )


def _build_domain_accounts(
    db: Session,
    transactions: list[ObservedTransaction],
) -> dict[str, Cuenta]:
    accounts = {
        snapshot.account_number: _domain_account_from_snapshot(snapshot)
        for snapshot in db.query(ObservedAccount).all()
    }

    for transaction in transactions:
        domain_transaction = _domain_transaction_from_observed(transaction)
        endpoints = [
            (transaction.source_account_number, transaction.source_bank_code),
            (transaction.destination_account_number, transaction.destination_bank_code),
        ]
        for account_number, bank_code in endpoints:
            if account_number not in accounts:
                accounts[account_number] = _domain_account_from_transaction(
                    account_number,
                    bank_code,
                    transaction.created_at,
                    transaction.location or "",
                )
            accounts[account_number].registrar_transaccion(domain_transaction)

    return accounts


def _persist_account_protection(
    db: Session,
    accounts: dict[str, Cuenta],
) -> None:
    for snapshot in db.query(ObservedAccount).all():
        account = accounts.get(snapshot.account_number)
        snapshot.data_protected_by_investigation = bool(
            account and account.datos_protegidos_por_investigacion
        )
        db.add(snapshot)


def _persist_alerts(db: Session, alerts: list[ResultadoRegla]) -> None:
    for alert in alerts:
        db.add(
            RiskAlert(
                observed_transaction_id=alert.observed_transaction_id,
                transaction_id=alert.transaction_id,
                account_number=alert.cuenta_numero,
                bank_code=alert.bank_code,
                category=alert.category,
                score=alert.score_riesgo,
                level=_score_to_level(alert.score_riesgo),
                reason=alert.motivo,
                pattern_type=alert.pattern_type,
                data_protection_applied=alert.data_protection_applied,
                created_at=alert.created_at,
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
    domain_accounts = _build_domain_accounts(db, transactions)
    alerts = MotorDeteccion().evaluar_cuentas(domain_accounts.values())

    _persist_account_protection(db, domain_accounts)
    _persist_alerts(db, alerts)
    db.commit()
    return len(alerts)


def list_alerts(
    db: Session,
    *,
    bank_code: str | None = None,
    account_number: str | None = None,
    level: str | None = None,
    category: str | None = None,
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
    if category:
        query = query.filter(RiskAlert.category == category)
    if pattern_type:
        query = query.filter(RiskAlert.pattern_type == pattern_type)

    protected_accounts = {
        item.account_number
        for item in db.query(ObservedAccount)
        .filter(ObservedAccount.data_protected_by_investigation.is_(True))
        .all()
    }

    return [
        RiskAlertResponse(
            id=alert.id,
            transaction_id=alert.transaction_id,
            account_number=alert.account_number,
            display_account_number=display_account_number(
                alert.account_number,
                protected_accounts,
            ),
            bank_code=alert.bank_code,
            category=alert.category,
            score=alert.score,
            level=alert.level,
            reason=alert.reason,
            pattern_type=alert.pattern_type,
            data_protection_applied=alert.data_protection_applied,
            created_at=alert.created_at,
        )
        for alert in query.limit(limit).all()
    ]


def get_alert_summary(db: Session) -> RiskAlertSummaryResponse:
    alerts = db.query(RiskAlert).all()
    by_level = Counter(alert.level for alert in alerts)
    by_pattern = Counter(alert.pattern_type for alert in alerts)
    by_category = Counter(alert.category for alert in alerts)
    return RiskAlertSummaryResponse(
        total_alerts=len(alerts),
        low=by_level.get("low", 0),
        medium=by_level.get("medium", 0),
        high=by_level.get("high", 0),
        critical=by_level.get("critical", 0),
        by_category=dict(sorted(by_category.items())),
        by_pattern=dict(sorted(by_pattern.items())),
    )
