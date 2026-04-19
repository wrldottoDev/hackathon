from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from ..database import Base


class LandingPage(Base):
    __tablename__ = "finsta_landing_pages"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    is_malicious = Column(Boolean, default=False, nullable=False)
    category = Column(String(50), default="unknown", nullable=False)
    days_since_creation = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
