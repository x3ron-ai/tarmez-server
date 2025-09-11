from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints
from .user import UserOut
from datetime import datetime

MessageContent = Annotated[str, StringConstraints(min_length=1, max_length=1000)]

class MessageBase(BaseModel):
	content: str

class MessageCreate(MessageBase):
	receiver_id: int

class MessageOut(MessageBase):
	id: int
	sender: UserOut
	receiver: UserOut
	created_at: datetime
	
	model_config = ConfigDict(from_attributes=True)