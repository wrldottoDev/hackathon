from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from ..database import Base


class BlacklistLink(Base):
    __tablename__ = "blacklist_links"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, unique=True, index=True)
    dominio = Column(String(255), nullable=True, index=True)
    ip_origen = Column(String(64), nullable=True, index=True)
    plataforma = Column(String(20), nullable=False, index=True)
    hits_reportados = Column(Integer, nullable=False, default=0)
    descripcion = Column(Text, nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
