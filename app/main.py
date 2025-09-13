from fastapi import FastAPI
from app.api import api_router
from app.db.session import Base, engine
import time

app = FastAPI(title="TarmeZ Messenger API")

app.include_router(api_router, prefix="/api")

@app.get("/time")
def time_route():
	return {"time":time.time()}

@app.get("/ping")
def ping_route():
	return {"msg": "pong"}
