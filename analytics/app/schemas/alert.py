from datetime import datetime

from pydantic import BaseModel


class RiskAlertResponse(BaseModel):
    id: int
    transaction_id: int
    account_number: str
    display_account_number: str
    bank_code: str
    category: str
    score: int
    level: str
    reason: str
    pattern_type: str
    data_protection_applied: bool
    created_at: datetime


class RiskAlertSummaryResponse(BaseModel):
    total_alerts: int
    low: int
    medium: int
    high: int
    critical: int
    by_category: dict[str, int]
    by_pattern: dict[str, int]
