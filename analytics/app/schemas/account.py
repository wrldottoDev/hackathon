from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .alert import RiskAlertResponse


class FollowUpTransaction(BaseModel):
    transaction_id: int
    bank_code: str
    source_account_number: str
    source_account_number_display: str
    destination_account_number: str
    destination_account_number_display: str
    amount: Decimal
    currency: str
    transaction_type: str
    status: str
    channel: str
    location: str | None = None
    beneficiary: str | None = None
    concept: str | None = None
    description: str | None = None
    source_balance_before: Decimal | None = None
    source_balance_after: Decimal | None = None
    created_at: datetime


class FollowUpCounterparty(BaseModel):
    account_number: str
    account_number_display: str
    bank_code: str
    direction: str
    transaction_count: int
    total_amount: Decimal


class NetworkPosition(BaseModel):
    incoming_edges: int
    outgoing_edges: int
    unique_counterparties: int
    indirect_counterparties: int


class AccountReportedUpdateRequest(BaseModel):
    reported: bool


class AccountFollowUpResponse(BaseModel):
    account_number: str
    account_number_display: str
    bank_code: str
    account_status: str
    current_balance: Decimal
    currency: str
    incoming_count: int
    outgoing_count: int
    total_incoming_amount: Decimal
    total_outgoing_amount: Decimal
    average_incoming_amount: Decimal
    average_outgoing_amount: Decimal
    high_amount_count: int
    last_activity_at: datetime | None = None
    last_credentials_change_at: datetime | None = None
    current_location: str | None = None
    location_history: list[str] = Field(default_factory=list)
    reported: bool = False
    data_protected_by_investigation: bool = False
    direct_counterparties: list[str]
    indirect_counterparties: list[str]
    frequent_counterparties: list[FollowUpCounterparty]
    alerts: list[RiskAlertResponse]
    recent_transactions: list[FollowUpTransaction]
    network_position: NetworkPosition
