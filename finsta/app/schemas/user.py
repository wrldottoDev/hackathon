from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    display_name: str
    bio: str = ""
    profile_picture_url: str = ""
    is_recruiter: bool = False
    is_verified: bool = False


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    bio: str
    profile_picture_url: str
    is_recruiter: bool
    is_verified: bool
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(UserResponse):
    risk_score: int | None = None
    risk_reasons: list[str] = []
