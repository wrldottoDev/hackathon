from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GeoLocation(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    precision_meters: float | None = None


class SecureBufferEvent(BaseModel):
    source: str
    origin_app: str
    payload: str
    timestamp: datetime


class DecryptedAlertReport(BaseModel):
    riesgo_probabilidad: float = Field(ge=0, le=1)
    ubicacion_gps: GeoLocation | None = None
    entidades_extraidas: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    buffer_texto: list[SecureBufferEvent] = Field(default_factory=list)
    origen_app: str | None = None
    creado_en: datetime | None = None


class EncryptedAlertEnvelope(BaseModel):
    algorithm: str = Field(default="RSA-OAEP-256/AES-256-GCM")
    key_fingerprint: str = Field(min_length=64, max_length=64)
    encrypted_key: str = Field(min_length=32)
    nonce: str = Field(min_length=8)
    ciphertext: str = Field(min_length=8)
    mac: str = Field(min_length=8)


class SecureAlertReceiptResponse(BaseModel):
    id: int
    hash_denuncia: str
    recibo_inmutabilidad: str
    timestamp: datetime
    estado_investigacion: str


class SecureAlertDetailResponse(SecureAlertReceiptResponse):
    ubicacion_gps: str
    entidades_extraidas: list[str]
    metadata_reporte: dict[str, Any]
    buffer_texto: list[dict[str, Any]]
    origen_app: str | None = None
    riesgo_probabilidad: str
