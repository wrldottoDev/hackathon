from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from ..database import Base


class FinstaAlert(Base):
    __tablename__ = "finsta_alerts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(20), default="finsta", nullable=False)
    category = Column(String(50), index=True, nullable=False)
    pattern_type = Column(String(50), index=True, nullable=False)
    score = Column(Integer, nullable=False)
    level = Column(String(20), index=True, nullable=False)
    reason = Column(Text, nullable=False)
    username = Column(String(50), index=True, nullable=False)
    target_type = Column(String(20), nullable=False)
    target_id = Column(Integer, nullable=False)
    rules_triggered = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
