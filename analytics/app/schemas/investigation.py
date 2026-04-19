from datetime import datetime

from pydantic import BaseModel, Field


class InvestigationCreate(BaseModel):
    account_number: str = Field(..., min_length=1, max_length=20)
    bank_code: str = Field(..., min_length=3, max_length=10)
    category: str
    priority: str = Field(default="medium")
    assigned_to: str | None = None
    notes: str | None = None


class InvestigationUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_to: str | None = None
    notes: str | None = None


class InvestigationResponse(BaseModel):
    id: int
    case_number: str
    account_number: str
    bank_code: str
    category: str
    status: str
    priority: str
    assigned_to: str | None
    notes: str | None
    risk_score: int
    pattern_types: list[str]
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None


class InvestigationSummaryResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    escalated: int
    closed: int
    by_category: dict[str, int]
    by_priority: dict[str, int]
