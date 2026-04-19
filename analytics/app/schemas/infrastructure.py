from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BlacklistLinkCreate(BaseModel):
    url: str
    ip_origen: str | None = None
    plataforma: str = Field(pattern="^(FB|IG|Web)$")
    descripcion: str | None = None


class BlacklistLinkResponse(BaseModel):
    id: int
    url: str
    dominio: str | None = None
    ip_origen: str | None = None
    plataforma: str
    hits_reportados: int
    descripcion: str | None = None
    created_at: datetime


class SuspiciousAdCreate(BaseModel):
    url: str
    ip_origen: str | None = None
    plataforma: str = Field(pattern="^(FB|IG|Web)$")
    titulo: str | None = None
    descripcion: str | None = None


class SuspiciousAdResponse(BaseModel):
    id: int
    url: str
    dominio: str | None = None
    ip_origen: str | None = None
    plataforma: str
    hits_reportados: int
    titulo: str | None = None
    descripcion: str | None = None
    created_at: datetime


class HeatmapClusterResponse(BaseModel):
    cluster_id: str
    hit_count: int
    avg_risk: float
    centroid_latitude: float
    centroid_longitude: float
    alert_ids: list[int]
    region_bucket: str | None = None


class EvidenceDossierResponse(BaseModel):
    case_id: int
    expediente_generado_en: datetime
    case_summary: dict[str, Any]
    chat_alerts: list[dict[str, Any]]
    transacciones_financieras: list[dict[str, Any]]
    links_captacion: list[dict[str, Any]]
    mapa_ubicacion: dict[str, Any]
    hallazgos_gemini: dict[str, Any]
    rescue_mode: dict[str, Any]
