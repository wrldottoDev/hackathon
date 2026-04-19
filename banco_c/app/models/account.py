from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import relationship

from ..database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    bank_code = Column(String(10), default="BKC", nullable=False)
    balance = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    currency = Column(String(10), default="CRC", nullable=False)
    status = Column(String(20), default="active", nullable=False)
    last_activity_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_credentials_change_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    current_location = Column(String(255), default="", nullable=True)
    location_history = Column(JSON, default=list, nullable=False)
    data_protected_by_investigation = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("User", back_populates="accounts")
