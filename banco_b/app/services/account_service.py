import random
import string
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.money import ZERO_MONEY, to_money
from ..models.account import Account
from ..models.user import User
from ..settings import BANK_CODE


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
) -> Account:
    account = Account(
        account_number=_generate_account_number(db),
        user_id=user.id,
        bank_code=BANK_CODE,
        balance=to_money(initial_balance),
        currency="CRC",
        status="active",
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
