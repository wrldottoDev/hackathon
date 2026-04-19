from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "safecall_users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    assigned_simulated_number = Column(
        String(15), unique=True, index=True, nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    reports = relationship(
        "PhoneReport", back_populates="reporter", cascade="all, delete-orphan",
    )


class PhoneNumber(Base):
    __tablename__ = "safecall_phone_numbers"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(15), unique=True, index=True, nullable=False)
    carrier = Column(String(50), default="unknown")
    registered_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )
    total_reports = Column(Integer, default=0, nullable=False)
    last_reported_at = Column(DateTime, nullable=True)
    simulated_call_count_24h = Column(Integer, default=0, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    reports = relationship(
        "PhoneReport", back_populates="phone_number_rel", cascade="all, delete-orphan",
    )


class PhoneReport(Base):
    __tablename__ = "safecall_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(
        Integer, ForeignKey("safecall_users.id"), nullable=False, index=True,
    )
    phone_number_id = Column(
        Integer, ForeignKey("safecall_phone_numbers.id"), nullable=False, index=True,
    )
    reported_number = Column(String(15), index=True, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, default="")
    evidence_hash = Column(String(128), nullable=True)
    risk_level = Column(String(20), default="pending", nullable=False)
    consent_data_processing = Column(Boolean, default=False, nullable=False)
    reporter_ip_hash = Column(String(64), nullable=True)
    forwarded_to_analytics = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    reporter = relationship("User", back_populates="reports")
    phone_number_rel = relationship("PhoneNumber", back_populates="reports")
