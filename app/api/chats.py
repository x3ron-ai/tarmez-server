from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, aliased
from sqlalchemy import case, or_, select, desc, func
from app.db.session import get_db
from app.models.message import Message
from app.models.user import User
from app.api.users import get_current_user
from app.schemas.chat import ChatOut

router = APIRouter()


@router.get("/", response_model=list[ChatOut])
def list_chats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    partner_id = case(
        (Message.sender_id == user.id, Message.receiver_id), else_=Message.sender_id
    ).label("partner_id")

    row_number_col = (
        func.row_number()
        .over(partition_by=partner_id, order_by=desc(Message.created_at))
        .label("rn")
    )

    subq = (
        select(Message, partner_id, row_number_col)
        .filter(
            or_(Message.sender_id == user.id, Message.receiver_id == user.id),
            Message.deleted == False,
        )
        .subquery()
    )

    last_messages = aliased(Message, subq)
    partners = (
        db.query(User, last_messages)
        .join(subq, User.id == subq.c.partner_id)
        .filter(subq.c.rn == 1)
        .all()
    )

    chats_out = []
    for partner, last_message in partners:
        chats_out.append(
            ChatOut(id=partner.id, username=partner.username, last_message=last_message)
        )

    return chats_out
