from datetime import datetime

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    initial_balance: float = Field(default=0.0, ge=0)


class AccountResponse(BaseModel):
    id: int
    account_number: str
    bank_code: str
    balance: float
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
