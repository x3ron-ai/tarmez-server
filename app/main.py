from fastapi import FastAPI
from app.api import users, messages
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TarmeZ Messenger API")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])

@app.get("/")
def root():
	return {"msg": "tarmez up"}
