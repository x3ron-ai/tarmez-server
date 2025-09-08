from pydantic import BaseModel
from typing import Optional
from .message import MessageOut

class ChatOut(BaseModel):
	id: int
	username: str
	last_message: Optional[MessageOut]

	class Config:
		from_attributes = True
