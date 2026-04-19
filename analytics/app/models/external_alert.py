from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from ..database import Base


class ExternalAlert(Base):
    __tablename__ = "external_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)
    description = Column(Text, nullable=False)
    source_service = Column(String(30), index=True, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )
