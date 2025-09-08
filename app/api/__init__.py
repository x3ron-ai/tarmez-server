from fastapi import APIRouter
from . import users, messages, chats, ws

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(ws.router, prefix="/ws", tags=["ws"])