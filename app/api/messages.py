from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageOut
from app.api.users import get_current_user
from .ws import manager
from app.core.config import settings

router = APIRouter()


@router.post("/send", response_model=MessageOut, status_code=201)
async def send_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    msg = Message(content=payload.content, sender_id=user.id, receiver_id=receiver.id)
    db.add(msg)
    db.commit()
    db.refresh(msg, attribute_names=["sender", "receiver"])

    out = MessageOut.model_validate(msg)

    await manager.send_to_user(receiver.id, out.model_dump(mode="json"))
    await manager.send_to_user(user.id, out.model_dump(mode="json"))

    return out


@router.get("/with/{other_user_id}", response_model=list[MessageOut])
def get_messages_with_user(
    other_user_id: int,
    limit: int = settings.default_message_limit,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = (
        db.query(Message)
        .options(joinedload(Message.sender), joinedload(Message.receiver))
        .filter(
            (
                (Message.sender_id == current_user.id)
                & (Message.receiver_id == other_user_id)
            )
            | (
                (Message.sender_id == other_user_id)
                & (Message.receiver_id == current_user.id)
            )
        )
        .filter(Message.deleted == False)
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return list(reversed(messages))


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    if msg.sender_id != user.id:
        raise HTTPException(
            status_code=403, detail="Not allowed to delete this message"
        )

    msg.deleted = True
    db.add(msg)
    db.commit()
    return None
