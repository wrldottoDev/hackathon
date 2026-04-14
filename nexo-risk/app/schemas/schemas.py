from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# ── Transacciones ──────────────────────────────────────────────────────────────

class TransactionOut(BaseModel):
    id:          str
    ref:         str
    sender_id:   str
    receiver_id: str
    amount:      float
    currency:    str
    timestamp:   datetime
    channel:     str

    model_config = {"from_attributes": True}


# ── Cuentas ────────────────────────────────────────────────────────────────────

class AccountOut(BaseModel):
    id:         str
    code:       str
    name:       str
    country:    str
    risk_label: str

    model_config = {"from_attributes": True}


# ── Scoring ────────────────────────────────────────────────────────────────────

class SignalOut(BaseModel):
    code:        str
    triggered:   bool
    weight:      int
    score_added: float
    label:       str
    detail:      str


class ScoreResponse(BaseModel):
    account_id:     str
    account_code:   str
    score:          float
    risk_level:     str
    signals:        List[SignalOut]
    summary:        str
    recommendation: str


# ── Casos ──────────────────────────────────────────────────────────────────────

class CaseOut(BaseModel):
    id:             str
    ref:            str
    account_id:     str
    score:          float
    risk_level:     str
    signals:        List[str]        # nombres de señales disparadas
    summary:        str
    recommendation: str
    status:         str
    analyst_note:   Optional[str]
    created_at:     datetime
    reviewed_at:    Optional[datetime]

    model_config = {"from_attributes": True}


class CaseUpdateIn(BaseModel):
    status:       str           # reviewed / escalated / dismissed
    analyst_note: Optional[str] = ""


# ── Grafo de relaciones ────────────────────────────────────────────────────────

class GraphNode(BaseModel):
    id:         str
    code:       str
    risk_level: str


class GraphEdge(BaseModel):
    source:    str
    target:    str
    amount:    float
    timestamp: datetime


class GraphOut(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# ── Métricas del dashboard ─────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_cases:     int
    pending:         int
    high_risk:       int
    escalated:       int
    avg_score:       float
    top_signal:      str
