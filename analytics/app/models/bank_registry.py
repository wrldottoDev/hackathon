from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from ..database import Base


class BankRegistry(Base):
    __tablename__ = "bank_registry"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(255), nullable=False)
    bank_code = Column(String(10), unique=True, index=True, nullable=False)
    api_url = Column(String(255), nullable=False)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_fetched_at = Column(DateTime, nullable=True)

