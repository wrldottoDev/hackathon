from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.money import ZERO_MONEY, sum_money, to_money
from ..models.observed_transaction import ObservedTransaction
from ..schemas.account import (
    AccountFollowUpResponse,
    FollowUpCounterparty,
    FollowUpTransaction,
    NetworkPosition,
)
from .risk_service import HIGH_AMOUNT_THRESHOLD, list_alerts


def get_account_follow_up(db: Session, account_number: str) -> AccountFollowUpResponse:
    normalized_account = account_number.strip().upper()
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
    if not transactions:
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
            destination_account_number=transaction.destination_account_number,
            amount=to_money(transaction.amount),
            currency=transaction.currency,
            transaction_type=transaction.transaction_type,
            status=transaction.status,
            channel=transaction.channel,
            location=transaction.location,
            description=transaction.description,
            created_at=transaction.created_at,
        )
        for transaction in transactions[:20]
    ]

    return AccountFollowUpResponse(
        account_number=normalized_account,
        bank_code=normalized_account.split("-", 1)[0],
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
            1 for item in transactions if item.amount >= HIGH_AMOUNT_THRESHOLD
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
