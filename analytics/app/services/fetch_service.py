from __future__ import annotations

from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..core.money import to_money
from ..models.bank_registry import BankRegistry
from ..models.observed_transaction import ObservedTransaction
from ..schemas.transaction import FetchTransactionsResponse
from ..settings import FETCH_TIMEOUT_SECONDS, SERVICE_TOKEN
from .risk_service import recompute_risk_alerts


def _service_headers() -> dict[str, str]:
    return {"X-Service-Token": SERVICE_TOKEN}


def _upsert_observed_transaction(
    db: Session,
    *,
    bank_code: str,
    payload: dict,
    fetched_at: datetime,
) -> tuple[ObservedTransaction, bool]:
    transaction = (
        db.query(ObservedTransaction)
        .filter(
            ObservedTransaction.bank_code == bank_code,
            ObservedTransaction.external_transaction_id == payload["id"],
        )
        .first()
    )
    created = transaction is None
    if transaction is None:
        transaction = ObservedTransaction(
            bank_code=bank_code,
            external_transaction_id=payload["id"],
        )
        db.add(transaction)

    transaction.source_account_number = payload["source_account_number"]
    transaction.destination_account_number = payload["destination_account_number"]
    transaction.source_bank_code = payload["source_bank_code"]
    transaction.destination_bank_code = payload["destination_bank_code"]
    transaction.amount = to_money(payload["amount"])
    transaction.currency = payload["currency"]
    transaction.transaction_type = payload["transaction_type"]
    transaction.status = payload["status"]
    transaction.channel = payload["channel"]
    transaction.location = payload.get("location") or ""
    transaction.description = payload.get("description") or ""
    transaction.external_reference = payload.get("external_reference")
    transaction.failure_reason = payload.get("failure_reason") or ""
    transaction.created_at = datetime.fromisoformat(payload["created_at"])
    transaction.fetched_at = fetched_at
    return transaction, created


def fetch_transactions_from_registered_banks(db: Session) -> FetchTransactionsResponse:
    banks = (
        db.query(BankRegistry)
        .filter(BankRegistry.status != "inactive")
        .order_by(BankRegistry.bank_code.asc())
        .all()
    )
    fetched_at = datetime.utcnow()
    transactions_seen = 0
    transactions_created = 0
    transactions_updated = 0

    with httpx.Client(timeout=FETCH_TIMEOUT_SECONDS) as client:
        for bank in banks:
            try:
                response = client.get(
                    f"{bank.api_url.rstrip('/')}/transactions/export",
                    headers=_service_headers(),
                    params={"limit": 1000},
                )
                response.raise_for_status()
                payload = response.json()
            except httpx.HTTPError:
                bank.status = "error"
                continue

            bank.status = "online"
            bank.last_fetched_at = fetched_at
            for item in payload:
                _, created = _upsert_observed_transaction(
                    db,
                    bank_code=bank.bank_code,
                    payload=item,
                    fetched_at=fetched_at,
                )
                transactions_seen += 1
                if created:
                    transactions_created += 1
                else:
                    transactions_updated += 1

    db.commit()
    alerts_generated = recompute_risk_alerts(db)
    return FetchTransactionsResponse(
        banks_processed=len(banks),
        transactions_seen=transactions_seen,
        transactions_created=transactions_created,
        transactions_updated=transactions_updated,
        alerts_generated=alerts_generated,
        fetched_at=fetched_at,
    )
