from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from ..database import Base


class SecureAlert(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    hash_denuncia = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    ubicacion_gps = Column(String(120), nullable=False, default="sin_datos")
    entidades_extraidas = Column(JSON, nullable=False, default=list)
    estado_investigacion = Column(String(32), nullable=False, default="pendiente")
    metadata_reporte = Column(JSON, nullable=False, default=dict)
    buffer_texto = Column(JSON, nullable=False, default=list)
    origen_app = Column(String(120), nullable=True)
    riesgo_probabilidad = Column(String(16), nullable=False, default="0.00")
    client_ip = Column(String(64), nullable=True)
    algorithm = Column(String(64), nullable=False, default="RSA-OAEP-256/AES-256-GCM")
    notas = Column(Text, nullable=True)
