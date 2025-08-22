from fastapi import FastAPI
from app.api import api_router
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TarmeZ Messenger API")

app.include_router(api_router, prefix="/api")

@app.get("/ping")
def root():
	return {"msg": "pong"}