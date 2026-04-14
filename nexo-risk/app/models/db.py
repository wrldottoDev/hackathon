from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Text, ForeignKey, Boolean
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


def new_id() -> str:
    return str(uuid.uuid4())


class Account(Base):
    __tablename__ = "accounts"

    id         = Column(String, primary_key=True, default=new_id)
    code       = Column(String, unique=True, nullable=False)   # e.g. ACC-0042
    name       = Column(String, nullable=False)
    country    = Column(String, default="CR")
    risk_label = Column(String, default="unknown")             # low/medium/high

    transactions_sent     = relationship("Transaction", foreign_keys="Transaction.sender_id",   back_populates="sender")
    transactions_received = relationship("Transaction", foreign_keys="Transaction.receiver_id", back_populates="receiver")


class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(String, primary_key=True, default=new_id)
    ref         = Column(String, unique=True, nullable=False)   # TXN-000001
    sender_id   = Column(String, ForeignKey("accounts.id"), nullable=False)
    receiver_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    amount      = Column(Float, nullable=False)
    currency    = Column(String, default="USD")
    timestamp   = Column(DateTime, nullable=False)
    channel     = Column(String, default="transfer")            # transfer/cash/mobile

    sender   = relationship("Account", foreign_keys=[sender_id],   back_populates="transactions_sent")
    receiver = relationship("Account", foreign_keys=[receiver_id], back_populates="transactions_received")


class Case(Base):
    __tablename__ = "cases"

    id           = Column(String, primary_key=True, default=new_id)
    ref          = Column(String, unique=True, nullable=False)  # CASE-00001
    account_id   = Column(String, ForeignKey("accounts.id"), nullable=False)
    score        = Column(Float, nullable=False)
    risk_level   = Column(String, nullable=False)               # low/medium/high/escalate
    signals      = Column(Text, nullable=False)                 # JSON list of signal names
    summary      = Column(Text, nullable=False)
    recommendation = Column(String, nullable=False)
    status       = Column(String, default="pending")            # pending/reviewed/escalated/dismissed
    analyst_note = Column(Text, default="")
    created_at   = Column(DateTime, default=datetime.utcnow)
    reviewed_at  = Column(DateTime, nullable=True)

    account = relationship("Account", foreign_keys=[account_id])
