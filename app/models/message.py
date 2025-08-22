from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Message(Base):
	__tablename__ = "messages"

	id = Column(Integer, primary_key=True, index=True)
	content = Column(String(1000), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now())

	user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
	user = relationship("User", backref="messages")