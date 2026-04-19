from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CorrelationRunRequest(BaseModel):
    lookback_hours: int = Field(default=24, ge=1, le=168)
    alert_limit: int = Field(default=20, ge=1, le=200)
    transaction_limit: int = Field(default=200, ge=1, le=500)


class GeminiCorrelationOutput(BaseModel):
    score_de_vinculacion: float = Field(ge=0, le=1)
    justificacion_tecnica: str = Field(min_length=20)
    coincidencias_financieras: list[str] = Field(default_factory=list)
    patron_muchas_a_una: list[str] = Field(default_factory=list)
    correlacion_geografica: str = Field(default="sin evidencia suficiente")
    beneficiarios_prioritarios: list[str] = Field(default_factory=list)


class ResolvedCaseResponse(BaseModel):
    id: int
    created_at: datetime
    period_start: datetime
    period_end: datetime
    score_de_vinculacion: float
    justificacion_tecnica: str
    hallazgos_json: dict[str, Any]
    alert_ids: list[int]
    transaction_ids: list[int]
    gemini_model: str
