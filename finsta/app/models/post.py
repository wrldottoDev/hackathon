from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Post(Base):
    __tablename__ = "finsta_posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("finsta_users.id"), nullable=False, index=True)
    image_url = Column(String(500), default="")
    caption = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    author = relationship("User", back_populates="posts")
    reports = relationship("Report", back_populates="post", cascade="all, delete-orphan")
