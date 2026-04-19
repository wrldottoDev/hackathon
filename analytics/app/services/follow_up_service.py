from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.money import ZERO_MONEY, sum_money, to_money
from ..models.observed_account import ObservedAccount
from ..models.observed_transaction import ObservedTransaction
from ..schemas.account import (
    AccountFollowUpResponse,
    FollowUpCounterparty,
    FollowUpTransaction,
    NetworkPosition,
)
from .privacy_service import display_account_number
from .risk_service import list_alerts

HIGH_VALUE_THRESHOLD = Decimal("10000.00")


def set_account_reported(
    db: Session,
    account_number: str,
    *,
    reported: bool,
) -> AccountFollowUpResponse:
    normalized_account = account_number.strip().upper()
    account_snapshot = (
        db.query(ObservedAccount)
        .filter(ObservedAccount.account_number == normalized_account)
        .first()
    )
    if account_snapshot is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada en analytics")

    account_snapshot.reported = reported
    db.add(account_snapshot)
    db.commit()

    from .risk_service import recompute_risk_alerts

    recompute_risk_alerts(db)
    return get_account_follow_up(db, normalized_account)


def get_account_follow_up(db: Session, account_number: str) -> AccountFollowUpResponse:
    normalized_account = account_number.strip().upper()
    account_snapshot = (
        db.query(ObservedAccount)
        .filter(ObservedAccount.account_number == normalized_account)
        .first()
    )
    protected_accounts = {
        item.account_number
        for item in db.query(ObservedAccount)
        .filter(ObservedAccount.data_protected_by_investigation.is_(True))
        .all()
    }
    transactions = (
        db.query(ObservedTransaction)
        .filter(
            ObservedTransaction.status == "completed",
            (ObservedTransaction.source_account_number == normalized_account)
            | (ObservedTransaction.destination_account_number == normalized_account),
        )
        .order_by(ObservedTransaction.created_at.desc(), ObservedTransaction.id.desc())
        .all()
    )
    if not transactions and account_snapshot is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada en analytics")

    outgoing = [
        transaction
        for transaction in transactions
        if transaction.source_account_number == normalized_account
    ]
    incoming = [
        transaction
        for transaction in transactions
        if transaction.destination_account_number == normalized_account
    ]

    direct_counterparties = sorted(
        {
            (
                transaction.destination_account_number
                if transaction.source_account_number == normalized_account
                else transaction.source_account_number
            )
            for transaction in transactions
        }
    )

    all_completed = (
        db.query(ObservedTransaction)
        .filter(ObservedTransaction.status == "completed")
        .all()
    )
    indirect_counterparties = sorted(
        {
            transaction.destination_account_number
            for transaction in all_completed
            if transaction.source_account_number in direct_counterparties
            and transaction.destination_account_number not in direct_counterparties
            and transaction.destination_account_number != normalized_account
        }
        | {
            transaction.source_account_number
            for transaction in all_completed
            if transaction.destination_account_number in direct_counterparties
            and transaction.source_account_number not in direct_counterparties
            and transaction.source_account_number != normalized_account
        }
    )

    counterparty_stats: dict[tuple[str, str], dict[str, object]] = defaultdict(
        lambda: {
            "transaction_count": 0,
            "total_amount": ZERO_MONEY,
            "direction": "mixed",
        }
    )
    for transaction in transactions:
        if transaction.source_account_number == normalized_account:
            counterparty = transaction.destination_account_number
            direction = "outgoing"
        else:
            counterparty = transaction.source_account_number
            direction = "incoming"

        key = (counterparty, counterparty.split("-", 1)[0])
        counterparty_stats[key]["transaction_count"] += 1
        counterparty_stats[key]["total_amount"] += transaction.amount
        previous_direction = counterparty_stats[key]["direction"]
        if previous_direction == "mixed" or previous_direction == direction:
            counterparty_stats[key]["direction"] = direction
        else:
            counterparty_stats[key]["direction"] = "mixed"

    frequent_counterparties = [
        FollowUpCounterparty(
            account_number=counterparty,
            account_number_display=display_account_number(
                counterparty,
                protected_accounts,
            ),
            bank_code=bank_code,
            direction=str(values["direction"]),
            transaction_count=int(values["transaction_count"]),
            total_amount=to_money(values["total_amount"]),
        )
        for (counterparty, bank_code), values in sorted(
            counterparty_stats.items(),
            key=lambda item: (
                -int(item[1]["transaction_count"]),
                -item[1]["total_amount"],
                item[0][0],
            ),
        )[:10]
    ]

    recent_transactions = [
        FollowUpTransaction(
            transaction_id=transaction.external_transaction_id,
            bank_code=transaction.bank_code,
            source_account_number=transaction.source_account_number,
            source_account_number_display=display_account_number(
                transaction.source_account_number,
                protected_accounts,
            ),
            destination_account_number=transaction.destination_account_number,
            destination_account_number_display=display_account_number(
                transaction.destination_account_number,
                protected_accounts,
            ),
            amount=to_money(transaction.amount),
            currency=transaction.currency,
            transaction_type=transaction.transaction_type,
            status=transaction.status,
            channel=transaction.channel,
            location=transaction.location,
            beneficiary=transaction.beneficiary,
            concept=transaction.concept,
            description=transaction.description,
            source_balance_before=to_money(transaction.source_balance_before)
            if transaction.source_balance_before is not None
            else None,
            source_balance_after=to_money(transaction.source_balance_after)
            if transaction.source_balance_after is not None
            else None,
            created_at=transaction.created_at,
        )
        for transaction in transactions[:20]
    ]

    current_balance = (
        to_money(account_snapshot.balance)
        if account_snapshot is not None
        else ZERO_MONEY
    )
    account_status = account_snapshot.status if account_snapshot is not None else "unknown"
    currency = account_snapshot.currency if account_snapshot is not None else "CRC"
    current_location = (
        account_snapshot.current_location
        if account_snapshot is not None
        else (transactions[0].location if transactions else "")
    )
    location_history = (
        list(account_snapshot.location_history or [])
        if account_snapshot is not None
        else [
            transaction.location
            for transaction in reversed(transactions)
            if transaction.location
        ]
    )

    return AccountFollowUpResponse(
        account_number=normalized_account,
        account_number_display=display_account_number(
            normalized_account,
            protected_accounts,
        ),
        bank_code=normalized_account.split("-", 1)[0],
        account_status=account_status,
        current_balance=current_balance,
        currency=currency,
        incoming_count=len(incoming),
        outgoing_count=len(outgoing),
        total_incoming_amount=sum_money(item.amount for item in incoming),
        total_outgoing_amount=sum_money(item.amount for item in outgoing),
        average_incoming_amount=to_money(
            sum_money(item.amount for item in incoming) / len(incoming),
        )
        if incoming
        else ZERO_MONEY,
        average_outgoing_amount=to_money(
            sum_money(item.amount for item in outgoing) / len(outgoing),
        )
        if outgoing
        else ZERO_MONEY,
        high_amount_count=sum(
            1 for item in transactions if item.amount >= HIGH_VALUE_THRESHOLD
        ),
        last_activity_at=account_snapshot.last_activity_at if account_snapshot else None,
        last_credentials_change_at=(
            account_snapshot.last_credentials_change_at if account_snapshot else None
        ),
        current_location=current_location,
        location_history=location_history,
        reported=bool(account_snapshot and getattr(account_snapshot, "reported", False)),
        data_protected_by_investigation=bool(
            account_snapshot and account_snapshot.data_protected_by_investigation
        ),
        direct_counterparties=direct_counterparties,
        indirect_counterparties=indirect_counterparties,
        frequent_counterparties=frequent_counterparties,
        alerts=list_alerts(db, account_number=normalized_account, limit=100),
        recent_transactions=recent_transactions,
        network_position=NetworkPosition(
            incoming_edges=len({item.source_account_number for item in incoming}),
            outgoing_edges=len({item.destination_account_number for item in outgoing}),
            unique_counterparties=len(direct_counterparties),
            indirect_counterparties=len(indirect_counterparties),
        ),
    )
