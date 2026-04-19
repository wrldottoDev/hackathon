from datetime import datetime, timezone
import random
import string
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.money import ZERO_MONEY, to_money
from ..models.account import Account
from ..models.user import User
from ..settings import BANK_CODE


def _normalize_location(location: str | None) -> str:
    if not location:
        return ""
    return location.strip()


def _generate_account_number(db: Session) -> str:
    while True:
        digits = "".join(random.choices(string.digits, k=10))
        number = f"{BANK_CODE}-{digits}"
        if not db.query(Account).filter(Account.account_number == number).first():
            return number


def create_account(
    db: Session,
    user: User,
    initial_balance: Decimal | int | float | str = ZERO_MONEY,
    *,
    current_location: str = "",
) -> Account:
    now = datetime.now(timezone.utc)
    normalized_location = _normalize_location(current_location)
    account = Account(
        account_number=_generate_account_number(db),
        user_id=user.id,
        bank_code=BANK_CODE,
        balance=to_money(initial_balance),
        currency="CRC",
        status="active",
        last_activity_at=now,
        last_credentials_change_at=now,
        current_location=normalized_location,
        location_history=[normalized_location] if normalized_location else [],
        data_protected_by_investigation=False,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_accounts_by_user(db: Session, user: User) -> list[Account]:
    return db.query(Account).filter(Account.user_id == user.id).all()


def get_account_by_id(db: Session, account_id: int, user: User) -> Account:
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == user.id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return account


def get_accounts_for_export(db: Session) -> list[Account]:
    return (
        db.query(Account)
        .order_by(Account.created_at.asc(), Account.id.asc())
        .all()
    )


def mark_simulated_pin_change(
    db: Session,
    account_id: int,
    user: User,
    *,
    location: str = "",
) -> Account:
    account = get_account_by_id(db, account_id, user)
    now = datetime.now(timezone.utc)
    normalized_location = _normalize_location(location)

    account.last_credentials_change_at = now
    account.last_activity_at = now
    if normalized_location:
        history = list(account.location_history or [])
        if not history or history[-1] != normalized_location:
            history.append(normalized_location)
        account.current_location = normalized_location
        account.location_history = history[-20:]

    db.add(account)
    db.commit()
    db.refresh(account)
    return account
