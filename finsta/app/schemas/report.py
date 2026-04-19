from datetime import datetime

from pydantic import BaseModel


class ReportCreate(BaseModel):
    reported_user_id: int | None = None
    post_id: int | None = None
    message_id: int | None = None
    reason: str
    description: str = ""


class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    reported_user_id: int | None
    post_id: int | None
    message_id: int | None
    reason: str
    description: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
