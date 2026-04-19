from decimal import Decimal

from pydantic import BaseModel


class RiskAccountSummary(BaseModel):
    account_number: str
    bank_code: str
    max_score: int
    level: str
    alert_count: int
    pattern_types: list[str]
    categories: list[str]


class GeographicHotspot(BaseModel):
    location: str
    alert_count: int
    avg_score: float
    dominant_category: str


class HourlyDistribution(BaseModel):
    hour: int
    transaction_count: int
    alert_count: int
    total_amount: Decimal


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    avg_score: float
    top_pattern: str


class DashboardResponse(BaseModel):
    total_accounts: int
    total_transactions: int
    total_alerts: int
    active_investigations: int
    alerts_by_level: dict[str, int]
    alerts_by_category: list[CategoryBreakdown]
    top_risk_accounts: list[RiskAccountSummary]
    geographic_hotspots: list[GeographicHotspot]
    hourly_distribution: list[HourlyDistribution]
    pattern_distribution: dict[str, int]
