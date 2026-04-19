from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from ..database import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    account_number = Column(String(20), index=True, nullable=False)
    bank_code = Column(String(10), index=True, nullable=False)
    category = Column(String(30), nullable=False)
    status = Column(String(20), default="open", nullable=False, index=True)
    priority = Column(String(20), nullable=False, index=True)
    assigned_to = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    risk_score = Column(Integer, nullable=False)
    pattern_types = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    closed_at = Column(DateTime, nullable=True)
