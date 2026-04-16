from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class BankRegistryCreate(BaseModel):
    bank_name: str = Field(min_length=3, max_length=255)
    bank_code: str = Field(min_length=3, max_length=10)
    api_url: str = Field(min_length=10, max_length=255)
    status: str = Field(default="active", min_length=4, max_length=20)

    @field_validator("bank_name", "status", "api_url", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("bank_code", mode="before")
    @classmethod
    def normalize_bank_code(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip().upper()

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return value.rstrip("/")


class BankRegistryResponse(BaseModel):
    id: int
    bank_name: str
    bank_code: str
    api_url: str
    status: str
    created_at: datetime
    last_fetched_at: datetime | None = None

    model_config = {"from_attributes": True}

