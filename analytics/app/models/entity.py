from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from ..database import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    identifier = Column(String(100), unique=True, nullable=False, index=True)
    risk_level = Column(String(20), default="unknown", nullable=False)
    associated_accounts = Column(JSON, default=list, nullable=False)
    flags = Column(JSON, default=list, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
