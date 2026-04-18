from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text

from ..database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    source_account_number = Column(String(20), nullable=False, index=True)
    destination_account_number = Column(String(20), nullable=False, index=True)
    source_bank_code = Column(String(10), nullable=False)
    destination_bank_code = Column(String(10), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), default="CRC", nullable=False)
    transaction_type = Column(String(50), default="internal_transfer", nullable=False)
    status = Column(String(20), default="completed", nullable=False)
    channel = Column(String(50), default="web", nullable=False)
    location = Column(String(255), default="", nullable=True)
    description = Column(Text, default="", nullable=True)
    external_reference = Column(String(100), index=True, nullable=True)
    failure_reason = Column(Text, default="", nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
