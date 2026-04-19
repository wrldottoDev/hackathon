from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, Numeric, String, UniqueConstraint

from ..database import Base


class ObservedAccount(Base):
    __tablename__ = "observed_accounts"
    __table_args__ = (
        UniqueConstraint(
            "bank_code",
            "account_number",
            name="uq_observed_account_bank_account",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    bank_code = Column(String(10), index=True, nullable=False)
    account_number = Column(String(20), index=True, nullable=False)
    balance = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(String(20), index=True, nullable=False)
    last_activity_at = Column(DateTime, nullable=True)
    last_credentials_change_at = Column(DateTime, nullable=True)
    current_location = Column(String(255), nullable=True)
    location_history = Column(JSON, default=list, nullable=False)
    reported = Column(Boolean, default=False, nullable=False)
    data_protected_by_investigation = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
