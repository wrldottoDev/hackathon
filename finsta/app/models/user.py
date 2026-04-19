from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    __tablename__ = "finsta_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    bio = Column(Text, default="")
    profile_picture_url = Column(String(500), default="")
    is_recruiter = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    sent_messages = relationship(
        "DirectMessage",
        back_populates="sender",
        foreign_keys="DirectMessage.sender_id",
        cascade="all, delete-orphan",
    )
    received_messages = relationship(
        "DirectMessage",
        back_populates="recipient",
        foreign_keys="DirectMessage.recipient_id",
        cascade="all, delete-orphan",
    )
    reports_filed = relationship(
        "Report",
        back_populates="reporter",
        foreign_keys="Report.reporter_id",
        cascade="all, delete-orphan",
    )
