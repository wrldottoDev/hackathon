from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from .alert import RiskAlertResponse


class FollowUpTransaction(BaseModel):
    transaction_id: int
    bank_code: str
    source_account_number: str
    destination_account_number: str
    amount: Decimal
    currency: str
    transaction_type: str
    status: str
    channel: str
    location: str | None = None
    description: str | None = None
    created_at: datetime


class FollowUpCounterparty(BaseModel):
    account_number: str
    bank_code: str
    direction: str
    transaction_count: int
    total_amount: Decimal


class NetworkPosition(BaseModel):
    incoming_edges: int
    outgoing_edges: int
    unique_counterparties: int
    indirect_counterparties: int


class AccountFollowUpResponse(BaseModel):
    account_number: str
    bank_code: str
    incoming_count: int
    outgoing_count: int
    total_incoming_amount: Decimal
    total_outgoing_amount: Decimal
    average_incoming_amount: Decimal
    average_outgoing_amount: Decimal
    high_amount_count: int
    direct_counterparties: list[str]
    indirect_counterparties: list[str]
    frequent_counterparties: list[FollowUpCounterparty]
    alerts: list[RiskAlertResponse]
    recent_transactions: list[FollowUpTransaction]
    network_position: NetworkPosition
