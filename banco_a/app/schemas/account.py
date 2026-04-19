from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class AccountCreate(BaseModel):
    initial_balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=14,
        decimal_places=2,
    )
    current_location: str = Field(default="", max_length=255)

    @field_validator("current_location", mode="before")
    @classmethod
    def normalize_location(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()


class SimulatePinChangeRequest(BaseModel):
    location: str = Field(default="", max_length=255)

    @field_validator("location", mode="before")
    @classmethod
    def normalize_pin_location(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()


class AccountResponse(BaseModel):
    id: int
    account_number: str
    bank_code: str
    balance: Decimal
    currency: str
    status: str
    last_activity_at: datetime
    last_credentials_change_at: datetime
    current_location: str | None = None
    location_history: list[str] = Field(default_factory=list)
    data_protected_by_investigation: bool
    created_at: datetime

    model_config = {"from_attributes": True}
