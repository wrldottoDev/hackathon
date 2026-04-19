from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: str = Field(..., max_length=255)


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    assigned_simulated_number: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    reporter_id: int
    reported_number: str = Field(..., pattern=r"^\+506\s?8\d{3}-?\d{4}$")
    category: str = Field(..., min_length=2, max_length=50)
    description: str = ""
    evidence_hash: Optional[str] = None
    consent_data_processing: bool = False


class ReportOut(BaseModel):
    id: int
    reporter_id: int
    reported_number: str
    category: str
    description: str
    evidence_hash: Optional[str]
    risk_level: str
    consent_data_processing: bool
    forwarded_to_analytics: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ScoringOut(BaseModel):
    score: int
    risk_level: str
    fraud_category: str
    total_reports: int
    recent_reports_7d: int
    simulated_call_volume: int
    number_age_days: int
    factors: list[str]


class LookupResponse(BaseModel):
    number: str
    carrier: str
    is_blocked: bool
    status_message: str
    scoring: ScoringOut
    recent_reports: list[ReportOut]


class PhoneNumberSummary(BaseModel):
    number: str
    carrier: str
    total_reports: int
    is_blocked: bool
    risk_level: str
    status_message: str
