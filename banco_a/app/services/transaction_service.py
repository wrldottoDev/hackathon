from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.money import to_money
from ..models.account import Account
from ..models.transaction import Transaction
from ..models.user import User
from ..schemas.transaction import (
    InterbankReceiveRequest,
    InterbankReversalRequest,
    TransferRequest,
)
from ..settings import (
    BANK_CODE,
    BANK_REGISTRY,
    INTERBANK_TIMEOUT_SECONDS,
    SERVICE_TOKEN,
)


def _round_money(amount: Decimal | int | float | str) -> Decimal:
    return to_money(amount)


def _parse_bank_code(account_number: str) -> str:
    parts = account_number.split("-", 1)
    if len(parts) != 2 or not parts[0]:
        raise HTTPException(
            status_code=400,
            detail=f"Número de cuenta inválido: {account_number}",
        )
    return parts[0].upper()


def _get_account(db: Session, account_number: str) -> Account | None:
    return (
        db.query(Account)
        .filter(Account.account_number == account_number)
        .first()
    )


def _get_active_account(db: Session, account_number: str) -> Account:
    account = (
        db.query(Account)
        .filter(
            Account.account_number == account_number,
            Account.status == "active",
        )
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Cuenta {account_number} no encontrada o inactiva",
        )
    return account


def _resolve_remote_bank_url(bank_code: str) -> str:
    if bank_code == BANK_CODE:
        raise HTTPException(
            status_code=400,
            detail="La transferencia interbancaria requiere un banco destino diferente",
        )
    api_url = BANK_REGISTRY.get(bank_code)
    if not api_url:
        raise HTTPException(
            status_code=400,
            detail=f"Banco destino no configurado: {bank_code}",
        )
    return api_url.rstrip("/")


def _service_headers() -> dict[str, str]:
    return {"X-Service-Token": SERVICE_TOKEN}


def _extract_response_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or "Respuesta inválida del servicio remoto"
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
    return "El servicio remoto rechazó la operación"


def _build_transaction(
    *,
    source_account_number: str,
    destination_account_number: str,
    source_bank_code: str,
    destination_bank_code: str,
    amount: Decimal,
    currency: str,
    transaction_type: str,
    status: str,
    channel: str,
    location: str,
    description: str,
    external_reference: str | None = None,
    failure_reason: str | None = None,
) -> Transaction:
    return Transaction(
        source_account_number=source_account_number,
        destination_account_number=destination_account_number,
        source_bank_code=source_bank_code,
        destination_bank_code=destination_bank_code,
        amount=_round_money(amount),
        currency=currency,
        transaction_type=transaction_type,
        status=status,
        channel=channel,
        location=location,
        description=description,
        external_reference=external_reference,
        failure_reason=failure_reason or "",
    )


def _record_failed_interbank_transaction(
    db: Session,
    data: TransferRequest,
    source: Account,
    destination_bank_code: str,
    external_reference: str,
    failure_reason: str,
) -> Transaction:
    transaction = _build_transaction(
        source_account_number=source.account_number,
        destination_account_number=data.destination_account_number,
        source_bank_code=BANK_CODE,
        destination_bank_code=destination_bank_code,
        amount=data.amount,
        currency=source.currency,
        transaction_type="interbank_outgoing",
        status="failed",
        channel=data.channel,
        location=data.location,
        description=data.description,
        external_reference=external_reference,
        failure_reason=failure_reason,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def create_internal_transfer(
    db: Session,
    data: TransferRequest,
    current_user: User,
) -> Transaction:
    if data.source_account_number == data.destination_account_number:
        raise HTTPException(
            status_code=400,
            detail="La cuenta origen y destino no pueden ser la misma",
        )

    source = _get_active_account(db, data.source_account_number)
    destination = _get_active_account(db, data.destination_account_number)

    if source.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No eres propietario de la cuenta origen",
        )
    if source.bank_code != BANK_CODE or destination.bank_code != BANK_CODE:
        raise HTTPException(
            status_code=400,
            detail="Ambas cuentas deben pertenecer a este banco para transferencias internas",
        )
    if source.balance < data.amount:
        raise HTTPException(
            status_code=400,
            detail="Saldo insuficiente",
        )

    try:
        source.balance = _round_money(source.balance - data.amount)
        destination.balance = _round_money(destination.balance + data.amount)
        transaction = _build_transaction(
            source_account_number=source.account_number,
            destination_account_number=destination.account_number,
            source_bank_code=BANK_CODE,
            destination_bank_code=BANK_CODE,
            amount=data.amount,
            currency=source.currency,
            transaction_type="internal_transfer",
            status="completed",
            channel=data.channel,
            location=data.location,
            description=data.description,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar la transferencia interna",
        ) from exc


def create_interbank_transfer(
    db: Session,
    data: TransferRequest,
    current_user: User,
) -> Transaction:
    if data.source_account_number == data.destination_account_number:
        raise HTTPException(
            status_code=400,
            detail="La cuenta origen y destino no pueden ser la misma",
        )

    source = _get_active_account(db, data.source_account_number)
    if source.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No eres propietario de la cuenta origen",
        )
    if source.balance < data.amount:
        raise HTTPException(
            status_code=400,
            detail="Saldo insuficiente",
        )

    destination_bank_code = _parse_bank_code(data.destination_account_number)
    if destination_bank_code == BANK_CODE:
        raise HTTPException(
            status_code=400,
            detail="Usa /transactions/internal para transferencias dentro del mismo banco",
        )

    destination_bank_url = _resolve_remote_bank_url(destination_bank_code)
    external_reference = uuid4().hex.upper()
    receive_payload = InterbankReceiveRequest(
        source_account_number=source.account_number,
        destination_account_number=data.destination_account_number,
        source_bank_code=BANK_CODE,
        amount=data.amount,
        currency=source.currency,
        channel=data.channel,
        location=data.location,
        description=data.description,
        external_reference=external_reference,
    )

    try:
        response = httpx.post(
            f"{destination_bank_url}/interbank/receive",
            json=receive_payload.model_dump(mode="json"),
            headers=_service_headers(),
            timeout=INTERBANK_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        failure_reason = "No se pudo comunicar con el banco destino"
        try:
            _record_failed_interbank_transaction(
                db,
                data,
                source,
                destination_bank_code,
                external_reference,
                failure_reason,
            )
        except Exception:
            db.rollback()
        raise HTTPException(status_code=502, detail=failure_reason) from exc

    if response.is_error:
        failure_reason = _extract_response_detail(response)
        try:
            _record_failed_interbank_transaction(
                db,
                data,
                source,
                destination_bank_code,
                external_reference,
                failure_reason,
            )
        except Exception:
            db.rollback()
        raise HTTPException(
            status_code=400 if 400 <= response.status_code < 500 else 502,
            detail=f"Banco destino rechazó la transferencia: {failure_reason}",
        )

    try:
        source.balance = _round_money(source.balance - data.amount)
        transaction = _build_transaction(
            source_account_number=source.account_number,
            destination_account_number=data.destination_account_number,
            source_bank_code=BANK_CODE,
            destination_bank_code=destination_bank_code,
            amount=data.amount,
            currency=source.currency,
            transaction_type="interbank_outgoing",
            status="completed",
            channel=data.channel,
            location=data.location,
            description=data.description,
            external_reference=external_reference,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except Exception as exc:
        db.rollback()
        reversal_succeeded = _reverse_remote_interbank_credit(
            destination_bank_url=destination_bank_url,
            external_reference=external_reference,
            reason="Compensación por fallo al confirmar en banco origen",
        )
        failure_reason = (
            "El banco destino acreditó los fondos, pero la operación se compensó en origen"
            if reversal_succeeded
            else "Se produjo un error crítico al confirmar la transferencia interbancaria"
        )
        try:
            _record_failed_interbank_transaction(
                db,
                data,
                source,
                destination_bank_code,
                external_reference,
                failure_reason,
            )
        except Exception:
            db.rollback()
        raise HTTPException(
            status_code=502 if reversal_succeeded else 500,
            detail=failure_reason,
        ) from exc


def _reverse_remote_interbank_credit(
    *,
    destination_bank_url: str,
    external_reference: str,
    reason: str,
) -> bool:
    payload = InterbankReversalRequest(
        external_reference=external_reference,
        reason=reason,
    )
    try:
        response = httpx.post(
            f"{destination_bank_url}/interbank/reverse",
            json=payload.model_dump(mode="json"),
            headers=_service_headers(),
            timeout=INTERBANK_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError:
        return False
    return response.is_success


def receive_interbank_transfer(
    db: Session,
    data: InterbankReceiveRequest,
) -> Transaction:
    existing = (
        db.query(Transaction)
        .filter(
            Transaction.external_reference == data.external_reference,
            Transaction.transaction_type == "interbank_incoming",
        )
        .first()
    )
    if existing:
        return existing

    if data.source_bank_code == BANK_CODE:
        raise HTTPException(
            status_code=400,
            detail="El banco origen debe ser diferente al banco destino",
        )

    destination = _get_active_account(db, data.destination_account_number)
    if destination.bank_code != BANK_CODE:
        raise HTTPException(
            status_code=400,
            detail="La cuenta destino no pertenece a este banco",
        )
    if destination.currency != data.currency:
        raise HTTPException(
            status_code=400,
            detail="La moneda de la cuenta destino no coincide con la transferencia",
        )

    try:
        destination.balance = _round_money(destination.balance + data.amount)
        transaction = _build_transaction(
            source_account_number=data.source_account_number,
            destination_account_number=destination.account_number,
            source_bank_code=data.source_bank_code,
            destination_bank_code=BANK_CODE,
            amount=data.amount,
            currency=data.currency,
            transaction_type="interbank_incoming",
            status="completed",
            channel=data.channel,
            location=data.location,
            description=data.description,
            external_reference=data.external_reference,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo acreditar la transferencia interbancaria",
        ) from exc


def reverse_interbank_transfer(
    db: Session,
    data: InterbankReversalRequest,
) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.external_reference == data.external_reference,
            Transaction.transaction_type == "interbank_incoming",
        )
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="No existe una transferencia interbancaria para revertir",
        )
    if transaction.status == "reversed":
        return transaction

    destination = _get_account(db, transaction.destination_account_number)
    if not destination:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la cuenta destino para revertir la operación",
        )
    if destination.balance < transaction.amount:
        raise HTTPException(
            status_code=409,
            detail="No se puede revertir la operación porque el saldo disponible es insuficiente",
        )

    try:
        destination.balance = _round_money(destination.balance - transaction.amount)
        transaction.status = "reversed"
        transaction.failure_reason = data.reason
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo revertir la transferencia interbancaria",
        ) from exc


def get_transactions_by_user(db: Session, user: User) -> list[Transaction]:
    account_numbers = [
        account.account_number
        for account in db.query(Account).filter(Account.user_id == user.id).all()
    ]
    if not account_numbers:
        return []

    return (
        db.query(Transaction)
        .filter(
            (Transaction.source_account_number.in_(account_numbers))
            | (Transaction.destination_account_number.in_(account_numbers))
        )
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .all()
    )


def get_transactions_for_export(
    db: Session,
    since: datetime | None = None,
    limit: int = 500,
) -> list[Transaction]:
    query = db.query(Transaction).order_by(Transaction.created_at.asc(), Transaction.id.asc())
    if since is not None:
        query = query.filter(Transaction.created_at >= since)
    return query.limit(limit).all()
