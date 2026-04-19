from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.message import DirectMessage
from ..models.user import User
from ..schemas.message import MessageCreate, MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])


def _enrich_message(db: Session, msg: DirectMessage) -> MessageResponse:
    sender = db.query(User).filter(User.id == msg.sender_id).first()
    recipient = db.query(User).filter(User.id == msg.recipient_id).first()
    return MessageResponse(
        id=msg.id,
        sender_id=msg.sender_id,
        sender_username=sender.username if sender else "",
        recipient_id=msg.recipient_id,
        recipient_username=recipient.username if recipient else "",
        body=msg.body,
        is_read=msg.is_read,
        created_at=msg.created_at,
    )


@router.post("", response_model=MessageResponse, status_code=201)
def send_message(
    sender_id: int = Query(...),
    payload: MessageCreate = ...,
    db: Session = Depends(get_db),
):
    sender = db.query(User).filter(User.id == sender_id).first()
    if not sender:
        raise HTTPException(404, "Sender not found")
    recipient = db.query(User).filter(User.id == payload.recipient_id).first()
    if not recipient:
        raise HTTPException(404, "Recipient not found")
    msg = DirectMessage(sender_id=sender_id, recipient_id=payload.recipient_id, body=payload.body)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _enrich_message(db, msg)


@router.get("/inbox/{user_id}", response_model=list[MessageResponse])
def get_inbox(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(DirectMessage)
        .filter(DirectMessage.recipient_id == user_id)
        .order_by(DirectMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_enrich_message(db, m) for m in messages]


@router.get("/conversation/{user_id}/{other_id}", response_model=list[MessageResponse])
def get_conversation(
    user_id: int,
    other_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(DirectMessage)
        .filter(
            or_(
                (DirectMessage.sender_id == user_id) & (DirectMessage.recipient_id == other_id),
                (DirectMessage.sender_id == other_id) & (DirectMessage.recipient_id == user_id),
            )
        )
        .order_by(DirectMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return [_enrich_message(db, m) for m in messages]


@router.patch("/{message_id}/read")
def mark_as_read(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(DirectMessage).filter(DirectMessage.id == message_id).first()
    if not msg:
        raise HTTPException(404, "Message not found")
    msg.is_read = True
    db.commit()
    return {"detail": "Marked as read"}
