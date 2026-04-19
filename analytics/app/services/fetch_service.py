from __future__ import annotations

from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..core.money import to_money
from ..models.bank_registry import BankRegistry
from ..models.observed_account import ObservedAccount
from ..models.observed_transaction import ObservedTransaction
from ..schemas.transaction import FetchTransactionsResponse
from ..settings import FETCH_TIMEOUT_SECONDS, SERVICE_TOKEN
from .risk_service import recompute_risk_alerts


def _service_headers() -> dict[str, str]:
    return {"X-Service-Token": SERVICE_TOKEN}


def _upsert_observed_account(
    db: Session,
    *,
    bank_code: str,
    payload: dict,
    fetched_at: datetime,
) -> tuple[ObservedAccount, bool]:
    account = (
        db.query(ObservedAccount)
        .filter(
            ObservedAccount.bank_code == bank_code,
            ObservedAccount.account_number == payload["account_number"],
        )
        .first()
    )
    created = account is None
    if account is None:
        account = ObservedAccount(
            bank_code=bank_code,
            account_number=payload["account_number"],
        )
        db.add(account)

    account.balance = to_money(payload["balance"])
    account.currency = payload["currency"]
    account.status = payload["status"]
    account.last_activity_at = datetime.fromisoformat(payload["last_activity_at"])
    account.last_credentials_change_at = datetime.fromisoformat(
        payload["last_credentials_change_at"]
    )
    account.current_location = payload.get("current_location") or ""
    account.location_history = payload.get("location_history") or []
    account.reported = bool(payload.get("reported", False))
    account.data_protected_by_investigation = bool(
        payload.get("data_protected_by_investigation", False)
    )
    account.created_at = datetime.fromisoformat(payload["created_at"])
    account.fetched_at = fetched_at
    return account, created


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
    transaction.beneficiary = payload.get("beneficiary") or payload["destination_account_number"]
    transaction.concept = payload.get("concept") or payload.get("description") or ""
    transaction.description = payload.get("description") or ""
    transaction.external_reference = payload.get("external_reference")
    transaction.failure_reason = payload.get("failure_reason") or ""
    transaction.source_balance_before = (
        to_money(payload["source_balance_before"])
        if payload.get("source_balance_before") is not None
        else None
    )
    transaction.source_balance_after = (
        to_money(payload["source_balance_after"])
        if payload.get("source_balance_after") is not None
        else None
    )
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
    accounts_seen = 0
    accounts_created = 0
    accounts_updated = 0
    transactions_seen = 0
    transactions_created = 0
    transactions_updated = 0

    with httpx.Client(timeout=FETCH_TIMEOUT_SECONDS) as client:
        for bank in banks:
            bank_online = False

            try:
                accounts_response = client.get(
                    f"{bank.api_url.rstrip('/')}/accounts/export",
                    headers=_service_headers(),
                )
                accounts_response.raise_for_status()
                accounts_payload = accounts_response.json()
                bank_online = True
                for item in accounts_payload:
                    _, created = _upsert_observed_account(
                        db,
                        bank_code=bank.bank_code,
                        payload=item,
                        fetched_at=fetched_at,
                    )
                    accounts_seen += 1
                    if created:
                        accounts_created += 1
                    else:
                        accounts_updated += 1
            except httpx.HTTPError:
                accounts_payload = []

            try:
                transactions_response = client.get(
                    f"{bank.api_url.rstrip('/')}/transactions/export",
                    headers=_service_headers(),
                    params={"limit": 1000},
                )
                transactions_response.raise_for_status()
                transactions_payload = transactions_response.json()
                bank_online = True
                for item in transactions_payload:
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
            except httpx.HTTPError:
                transactions_payload = []

            bank.status = "online" if bank_online else "error"
            if bank_online:
                bank.last_fetched_at = fetched_at

            del accounts_payload, transactions_payload

    db.commit()
    alerts_generated = recompute_risk_alerts(db)
    return FetchTransactionsResponse(
        banks_processed=len(banks),
        accounts_seen=accounts_seen,
        accounts_created=accounts_created,
        accounts_updated=accounts_updated,
        transactions_seen=transactions_seen,
        transactions_created=transactions_created,
        transactions_updated=transactions_updated,
        alerts_generated=alerts_generated,
        fetched_at=fetched_at,
    )
