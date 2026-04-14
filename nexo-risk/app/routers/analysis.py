"""
/analyze  — Evalúa una cuenta y crea/actualiza su caso de riesgo
/cases    — CRUD de casos para el analista
/graph    — Grafo de relaciones entre cuentas
"""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.db import Account, Case, Transaction
from app.schemas.schemas import (
    CaseOut, CaseUpdateIn, GraphOut, GraphNode, GraphEdge, ScoreResponse, SignalOut
)
from app.services.scoring import score_account

router = APIRouter(prefix="/api", tags=["analysis"])


# ── Helper ─────────────────────────────────────────────────────────────────────

def _case_counter(db: Session) -> str:
    n = db.query(Case).count() + 1
    return f"CASE-{n:05d}"


# ── Scoring / análisis ─────────────────────────────────────────────────────────

@router.post("/analyze/{account_id}", response_model=ScoreResponse)
def analyze_account(account_id: str, db: Session = Depends(get_db)):
    """Evalúa una cuenta y persiste el resultado como caso."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(404, "Cuenta no encontrada")

    result = score_account(account, db)

    # Actualizar risk_label en la cuenta
    account.risk_label = result.risk_level
    db.add(account)

    # Crear o actualizar el caso
    existing = (
        db.query(Case)
        .filter(Case.account_id == account_id, Case.status == "pending")
        .first()
    )

    triggered_labels = [s.label for s in result.signals if s.triggered]

    if existing:
        existing.score          = result.score
        existing.risk_level     = result.risk_level
        existing.signals        = json.dumps(triggered_labels)
        existing.summary        = result.summary
        existing.recommendation = result.recommendation
        db.add(existing)
    else:
        case = Case(
            ref=_case_counter(db),
            account_id=account_id,
            score=result.score,
            risk_level=result.risk_level,
            signals=json.dumps(triggered_labels),
            summary=result.summary,
            recommendation=result.recommendation,
        )
        db.add(case)

    db.commit()

    return ScoreResponse(
        account_id=result.account_id,
        account_code=result.account_code,
        score=result.score,
        risk_level=result.risk_level,
        signals=[SignalOut(**vars(s)) for s in result.signals],
        summary=result.summary,
        recommendation=result.recommendation,
    )


@router.post("/analyze/batch", response_model=List[ScoreResponse])
def analyze_all(db: Session = Depends(get_db)):
    """Analiza todas las cuentas en batch."""
    accounts = db.query(Account).all()
    results  = []
    for acc in accounts:
        result = score_account(acc, db)
        acc.risk_label = result.risk_level
        db.add(acc)
        triggered_labels = [s.label for s in result.signals if s.triggered]
        if result.score > 0:
            existing = (
                db.query(Case)
                .filter(Case.account_id == acc.id, Case.status == "pending")
                .first()
            )
            if existing:
                existing.score = result.score
                existing.risk_level = result.risk_level
                existing.signals = json.dumps(triggered_labels)
                existing.summary = result.summary
                existing.recommendation = result.recommendation
                db.add(existing)
            else:
                db.add(Case(
                    ref=_case_counter(db),
                    account_id=acc.id,
                    score=result.score,
                    risk_level=result.risk_level,
                    signals=json.dumps(triggered_labels),
                    summary=result.summary,
                    recommendation=result.recommendation,
                ))
        results.append(ScoreResponse(
            account_id=result.account_id,
            account_code=result.account_code,
            score=result.score,
            risk_level=result.risk_level,
            signals=[SignalOut(**vars(s)) for s in result.signals],
            summary=result.summary,
            recommendation=result.recommendation,
        ))
    db.commit()
    return results


# ── Casos ──────────────────────────────────────────────────────────────────────

def _case_to_out(c: Case) -> CaseOut:
    return CaseOut(
        id=c.id,
        ref=c.ref,
        account_id=c.account_id,
        score=c.score,
        risk_level=c.risk_level,
        signals=json.loads(c.signals),
        summary=c.summary,
        recommendation=c.recommendation,
        status=c.status,
        analyst_note=c.analyst_note,
        created_at=c.created_at,
        reviewed_at=c.reviewed_at,
    )


@router.get("/cases", response_model=List[CaseOut])
def list_cases(
    risk_level: Optional[str] = Query(None),
    status: Optional[str]     = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Case)
    if risk_level:
        q = q.filter(Case.risk_level == risk_level)
    if status:
        q = q.filter(Case.status == status)
    return [_case_to_out(c) for c in q.order_by(Case.score.desc()).all()]


@router.get("/cases/{case_id}", response_model=CaseOut)
def get_case(case_id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(404, "Caso no encontrado")
    return _case_to_out(c)


@router.patch("/cases/{case_id}", response_model=CaseOut)
def update_case(case_id: str, body: CaseUpdateIn, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(404, "Caso no encontrado")
    allowed = {"reviewed", "escalated", "dismissed"}
    if body.status not in allowed:
        raise HTTPException(400, f"Status debe ser uno de: {allowed}")
    c.status       = body.status
    c.analyst_note = body.analyst_note or ""
    c.reviewed_at  = datetime.utcnow()
    db.commit()
    return _case_to_out(c)


# ── Grafo de relaciones ────────────────────────────────────────────────────────

@router.get("/graph/{account_id}", response_model=GraphOut)
def get_graph(account_id: str, depth: int = Query(1, ge=1, le=2), db: Session = Depends(get_db)):
    """
    Devuelve nodos y aristas para la visualización del grafo.
    depth=1: cuentas directamente relacionadas
    depth=2: también las relacionadas de segundo nivel
    """
    root = db.query(Account).filter(Account.id == account_id).first()
    if not root:
        raise HTTPException(404, "Cuenta no encontrada")

    seen_accounts = {account_id: root}
    edges_raw: List[Transaction] = []

    frontier = {account_id}
    for _ in range(depth):
        next_frontier = set()
        for aid in frontier:
            txns = (
                db.query(Transaction)
                .filter(
                    (Transaction.sender_id == aid) | (Transaction.receiver_id == aid)
                )
                .all()
            )
            for t in txns:
                edges_raw.append(t)
                for nid in [t.sender_id, t.receiver_id]:
                    if nid not in seen_accounts:
                        acc = db.query(Account).filter(Account.id == nid).first()
                        if acc:
                            seen_accounts[nid] = acc
                            next_frontier.add(nid)
        frontier = next_frontier

    nodes = [
        GraphNode(id=a.id, code=a.code, risk_level=a.risk_label)
        for a in seen_accounts.values()
    ]

    # Deduplicar aristas
    seen_edges = set()
    edges = []
    for t in edges_raw:
        key = t.id
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append(GraphEdge(
                source=t.sender_id,
                target=t.receiver_id,
                amount=t.amount,
                timestamp=t.timestamp,
            ))

    return GraphOut(nodes=nodes, edges=edges)
