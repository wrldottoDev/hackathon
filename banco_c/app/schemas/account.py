from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    initial_balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=14,
        decimal_places=2,
    )


class AccountResponse(BaseModel):
    id: int
    account_number: str
    bank_code: str
    balance: Decimal
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
