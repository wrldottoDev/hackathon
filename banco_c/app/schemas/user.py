from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_MAX_LENGTH = 128
PasswordInput = Annotated[str, Field(max_length=PASSWORD_MAX_LENGTH)]


class UserCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    password: PasswordInput

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: PasswordInput


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
