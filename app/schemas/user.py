from pydantic import BaseModel

class UserBase(BaseModel):
	username: str

class UserCreate(UserBase):
	password: str

class UserLogin(UserBase):
	password: str

class UserOut(UserBase):
	id: int
	class Config:
		from_attributes = True

class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"

class TokenData(BaseModel):
	sub: int | None = None
