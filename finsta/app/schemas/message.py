from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    recipient_id: int
    body: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_username: str = ""
    recipient_id: int
    recipient_username: str = ""
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
