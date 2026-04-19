from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text

from ..database import Base


class ResolvedCase(Base):
    __tablename__ = "casos_resueltos"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    score_de_vinculacion = Column(Float, nullable=False, default=0.0)
    justificacion_tecnica = Column(Text, nullable=False)
    hallazgos_json = Column(JSON, nullable=False, default=dict)
    alert_ids = Column(JSON, nullable=False, default=list)
    transaction_ids = Column(JSON, nullable=False, default=list)
    gemini_model = Column(String(64), nullable=False)
    prompt_hash = Column(String(64), nullable=False, index=True)
