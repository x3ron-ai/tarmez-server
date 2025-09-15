from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints
from app.core.config import settings

class UserBase(BaseModel):
	username: str

PasswordStr = Annotated[
	str,
	StringConstraints(
		min_length=settings.password_min_length,
		max_length=settings.password_max_length,
	)
]

class UserCreate(UserBase):
	password: PasswordStr

class UserLogin(UserBase):
	password: str

class UserOut(UserBase):
	id: int

	model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"

class TokenData(BaseModel):
	sub: int | None = None
