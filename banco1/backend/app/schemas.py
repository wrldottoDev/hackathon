from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AccountCreate(BaseModel):
    initial_balance: float = Field(default=0.0, ge=0)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_number: str
    balance: float
    user_id: int
    created_at: datetime


class TransactionCreate(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: float = Field(gt=0)
    channel: str = Field(default="web", min_length=2, max_length=50)
    location: str = Field(default="San Jose, CR", min_length=2, max_length=255)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_account_id: int
    destination_account_id: int
    amount: float
    transaction_type: str
    status: str
    channel: str
    location: str
    created_at: datetime


class RiskAlertResponse(BaseModel):
    id: int
    transaction_id: int | None = None
    account_id: int | None = None
    score: int
    level: str
    reason: str
    created_at: datetime
    transaction_amount: float | None = None
    account_number: str | None = None


class RiskSummaryResponse(BaseModel):
    total_alerts: int
    low: int
    medium: int
    high: int
    latest_alerts: list[RiskAlertResponse]


class GraphNode(BaseModel):
    id: str
    label: str
    risk: str
    balance: float
    user_id: int
    owner_name: str
    account_number: str
    is_focus: bool = False
    transaction_count: int = 0


class GraphEdge(BaseModel):
    id: str
    transaction_id: int
    source: str
    target: str
    amount: float
    risk: str
    channel: str
    location: str
    created_at: datetime


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class NetworkReportTransaction(BaseModel):
    transaction_id: int
    source_account_id: int
    destination_account_id: int
    source_label: str
    destination_label: str
    amount: float
    risk: str
    channel: str
    location: str
    created_at: datetime


class NetworkReportCounterparty(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    transaction_count: int
    total_amount: float


class NetworkReportResponse(BaseModel):
    generated_at: datetime
    risk_filter: str
    user: UserResponse
    accounts: list[AccountResponse]
    total_transactions: int
    total_sent: float
    total_received: float
    distinct_counterparties: int
    flagged_transactions: int
    low: int
    medium: int
    high: int
    top_counterparties: list[NetworkReportCounterparty]
    recent_transactions: list[NetworkReportTransaction]
