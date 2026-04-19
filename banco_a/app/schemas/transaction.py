from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

ACCOUNT_NUMBER_PATTERN = r"^[A-Z]{3}-\d{10}$"


class TransferRequest(BaseModel):
    source_account_number: str = Field(
        min_length=14,
        max_length=14,
        pattern=ACCOUNT_NUMBER_PATTERN,
    )
    destination_account_number: str = Field(
        min_length=14,
        max_length=14,
        pattern=ACCOUNT_NUMBER_PATTERN,
    )
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    channel: str = Field(default="web", min_length=2, max_length=50)
    location: str = Field(default="", max_length=255)
    beneficiary: str = Field(default="", max_length=255)
    concept: str = Field(default="", max_length=500)
    description: str = Field(default="", max_length=500)

    @field_validator("source_account_number", "destination_account_number", mode="before")
    @classmethod
    def normalize_account_number(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip().upper()

    @field_validator("channel", "location", "beneficiary", "concept", "description", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()


class InterbankReceiveRequest(BaseModel):
    source_account_number: str = Field(
        min_length=14,
        max_length=14,
        pattern=ACCOUNT_NUMBER_PATTERN,
    )
    destination_account_number: str = Field(
        min_length=14,
        max_length=14,
        pattern=ACCOUNT_NUMBER_PATTERN,
    )
    source_bank_code: str = Field(min_length=3, max_length=10)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(default="CRC", min_length=3, max_length=10)
    channel: str = Field(default="api", min_length=2, max_length=50)
    location: str = Field(default="", max_length=255)
    beneficiary: str = Field(default="", max_length=255)
    concept: str = Field(default="", max_length=500)
    description: str = Field(default="", max_length=500)
    external_reference: str = Field(min_length=8, max_length=100)

    @field_validator(
        "source_account_number",
        "destination_account_number",
        "source_bank_code",
        "currency",
        "external_reference",
        mode="before",
    )
    @classmethod
    def normalize_upper_fields(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip().upper()

    @field_validator("channel", "location", "beneficiary", "concept", "description", mode="before")
    @classmethod
    def normalize_receive_text_fields(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()


class InterbankReversalRequest(BaseModel):
    external_reference: str = Field(min_length=8, max_length=100)
    reason: str = Field(default="Compensación de operación interbancaria", max_length=500)

    @field_validator("external_reference", mode="before")
    @classmethod
    def normalize_reference(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip().upper()

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()


class TransactionResponse(BaseModel):
    id: int
    source_account_number: str
    destination_account_number: str
    source_bank_code: str
    destination_bank_code: str
    amount: Decimal
    currency: str
    transaction_type: str
    status: str
    channel: str
    location: Optional[str]
    beneficiary: Optional[str]
    concept: Optional[str]
    description: Optional[str]
    external_reference: Optional[str]
    failure_reason: Optional[str]
    source_balance_before: Optional[Decimal]
    source_balance_after: Optional[Decimal]
    created_at: datetime

    model_config = {"from_attributes": True}
