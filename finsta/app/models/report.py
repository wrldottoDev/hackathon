from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Report(Base):
    __tablename__ = "finsta_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("finsta_users.id"), nullable=False, index=True)
    reported_user_id = Column(Integer, ForeignKey("finsta_users.id"), nullable=True, index=True)
    post_id = Column(Integer, ForeignKey("finsta_posts.id"), nullable=True, index=True)
    message_id = Column(Integer, ForeignKey("finsta_messages.id"), nullable=True, index=True)
    reason = Column(String(50), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    reporter = relationship("User", back_populates="reports_filed", foreign_keys=[reporter_id])
    reported_user = relationship("User", foreign_keys=[reported_user_id])
    post = relationship("Post", back_populates="reports")
    message = relationship("DirectMessage", back_populates="reports")
