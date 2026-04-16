from sqlalchemy.orm import Session

from ..models.bank_registry import BankRegistry
from ..schemas.bank import BankRegistryCreate


def upsert_bank(db: Session, data: BankRegistryCreate) -> BankRegistry:
    bank = db.query(BankRegistry).filter(BankRegistry.bank_code == data.bank_code).first()
    if bank:
        bank.bank_name = data.bank_name
        bank.api_url = data.api_url
        bank.status = data.status
    else:
        bank = BankRegistry(
            bank_name=data.bank_name,
            bank_code=data.bank_code,
            api_url=data.api_url,
            status=data.status,
        )
        db.add(bank)

    db.commit()
    db.refresh(bank)
    return bank


def list_banks(db: Session) -> list[BankRegistry]:
    return (
        db.query(BankRegistry)
        .order_by(BankRegistry.bank_code.asc())
        .all()
    )

