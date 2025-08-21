from fastapi import FastAPI
from app.api import users
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tarmes Messenger API")

app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def root():
	return {"msg": "tarmes up"}
