from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base


class ObservedTransaction(Base):
    __tablename__ = "observed_transactions"
    __table_args__ = (
        UniqueConstraint(
            "bank_code",
            "external_transaction_id",
            name="uq_observed_transaction_bank_external",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    bank_code = Column(String(10), index=True, nullable=False)
    external_transaction_id = Column(Integer, nullable=False)
    source_account_number = Column(String(20), index=True, nullable=False)
    destination_account_number = Column(String(20), index=True, nullable=False)
    source_bank_code = Column(String(10), nullable=False)
    destination_bank_code = Column(String(10), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    channel = Column(String(50), nullable=False)
    location = Column(String(255), nullable=True)
    beneficiary = Column(String(255), nullable=True)
    concept = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    external_reference = Column(String(100), nullable=True)
    failure_reason = Column(Text, nullable=True)
    source_balance_before = Column(Numeric(14, 2), nullable=True)
    source_balance_after = Column(Numeric(14, 2), nullable=True)
    created_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    risk_alerts = relationship(
        "RiskAlert",
        back_populates="observed_transaction",
        cascade="all, delete-orphan",
    )
