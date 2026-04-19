from datetime import datetime

from pydantic import BaseModel


class RuleResult(BaseModel):
    rule_name: str
    score: int
    detail: str


class AnalysisResult(BaseModel):
    target_type: str
    target_id: int
    user_id: int
    username: str
    total_score: int
    is_dangerous: bool
    risk_level: str
    rules_triggered: list[RuleResult]
    analyzed_at: datetime


class AnalysisSummary(BaseModel):
    total_analyzed_posts: int
    total_analyzed_messages: int
    total_dangerous_posts: int
    total_dangerous_messages: int
    dangerous_users: list[str]
    top_alerts: list[AnalysisResult]


class FinstaAlertForAnalytics(BaseModel):
    source: str = "finsta"
    category: str
    pattern_type: str
    score: int
    level: str
    reason: str
    username: str
    target_type: str
    target_id: int
    rules_triggered: list[RuleResult]
    created_at: datetime
