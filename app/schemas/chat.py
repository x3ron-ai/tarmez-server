from pydantic import BaseModel, ConfigDict
from typing import Optional
from .message import MessageOut

class ChatOut(BaseModel):
	id: int
	username: str
	last_message: Optional[MessageOut]

	model_config = ConfigDict(from_attributes=True)
