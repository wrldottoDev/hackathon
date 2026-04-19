from datetime import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    caption: str
    image_url: str = ""


class PostResponse(BaseModel):
    id: int
    author_id: int
    author_username: str = ""
    author_display_name: str = ""
    author_profile_picture: str = ""
    image_url: str
    caption: str
    likes_count: int
    reports_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
