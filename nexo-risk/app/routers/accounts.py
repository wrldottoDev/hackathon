from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from app.models.database import get_db
from app.models.db import Account, Transaction
from app.schemas.schemas import AccountOut, TransactionOut, DashboardStats
from app.models.db import Case
import json

router = APIRouter(prefix="/api", tags=["accounts"])


@router.get("/accounts", response_model=List[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.get("/accounts/{account_id}", response_model=AccountOut)
def get_account(account_id: str, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(404, "Cuenta no encontrada")
    return acc


@router.get("/accounts/{account_id}/transactions", response_model=List[TransactionOut])
def get_transactions(account_id: str, db: Session = Depends(get_db)):
    txns = (
        db.query(Transaction)
        .filter(
            (Transaction.sender_id == account_id) |
            (Transaction.receiver_id == account_id)
        )
        .order_by(Transaction.timestamp.desc())
        .all()
    )
    return txns


@router.post("/upload/transactions")
def upload_transactions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Carga transacciones desde CSV.
    Columnas requeridas: sender_code, receiver_code, amount, timestamp (ISO), channel
    """
    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))

    required = {"sender_code", "receiver_code", "amount", "timestamp"}
    missing  = required - set(df.columns)
    if missing:
        raise HTTPException(400, f"Columnas faltantes: {missing}")

    inserted = 0
    counter = db.query(Transaction).count() + 1

    for _, row in df.iterrows():
        # Obtener o crear cuentas
        def get_or_create(code: str) -> Account:
            acc = db.query(Account).filter(Account.code == code).first()
            if not acc:
                acc = Account(code=code, name=code, country="CR")
                db.add(acc)
                db.flush()
            return acc

        sender   = get_or_create(str(row["sender_code"]))
        receiver = get_or_create(str(row["receiver_code"]))

        ts = pd.to_datetime(row["timestamp"])
        txn = Transaction(
            ref=f"TXN-{counter:06d}",
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount=float(row["amount"]),
            currency=row.get("currency", "USD"),
            timestamp=ts.to_pydatetime(),
            channel=row.get("channel", "transfer"),
        )
        db.add(txn)
        counter += 1
        inserted += 1

    db.commit()
    return {"inserted": inserted}


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    if not cases:
        return DashboardStats(
            total_cases=0, pending=0, high_risk=0,
            escalated=0, avg_score=0.0, top_signal="—"
        )

    all_signals = []
    for c in cases:
        try:
            all_signals.extend(json.loads(c.signals))
        except Exception:
            pass

    top_signal = "—"
    if all_signals:
        top_signal = max(set(all_signals), key=all_signals.count)

    return DashboardStats(
        total_cases=len(cases),
        pending=sum(1 for c in cases if c.status == "pending"),
        high_risk=sum(1 for c in cases if c.risk_level in ("high", "escalate")),
        escalated=sum(1 for c in cases if c.status == "escalated"),
        avg_score=round(sum(c.score for c in cases) / len(cases), 1),
        top_signal=top_signal,
    )
