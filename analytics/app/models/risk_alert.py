from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    observed_transaction_id = Column(
        Integer,
        ForeignKey("observed_transactions.id"),
        nullable=False,
        index=True,
    )
    transaction_id = Column(Integer, nullable=False)
    account_number = Column(String(20), index=True, nullable=False)
    bank_code = Column(String(10), index=True, nullable=False)
    category = Column(String(30), index=True, nullable=False, default="aml")
    score = Column(Integer, nullable=False)
    level = Column(String(20), index=True, nullable=False)
    reason = Column(Text, nullable=False)
    pattern_type = Column(String(50), index=True, nullable=False)
    data_protection_applied = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    observed_transaction = relationship("ObservedTransaction", back_populates="risk_alerts")
