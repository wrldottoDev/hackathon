from datetime import datetime

from pydantic import BaseModel


class RiskAlertResponse(BaseModel):
    id: int
    transaction_id: int
    account_number: str
    bank_code: str
    score: int
    level: str
    reason: str
    pattern_type: str
    created_at: datetime


class RiskAlertSummaryResponse(BaseModel):
    total_alerts: int
    low: int
    medium: int
    high: int
    by_pattern: dict[str, int]

