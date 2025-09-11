import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from starlette.websockets import WebSocketDisconnect

client = TestClient(app)

@pytest.fixture
def users():
	u1 = {"username": f"ws_user1_{uuid.uuid4()}", "password": "pass1"}
	u2 = {"username": f"ws_user2_{uuid.uuid4()}", "password": "pass2"}

	assert client.post("/api/users/register", json=u1).status_code == 201
	assert client.post("/api/users/register", json=u2).status_code == 201

	r1 = client.post("/api/users/login", json=u1)
	r2 = client.post("/api/users/login", json=u2)
	token1 = r1.json()["access_token"]
	token2 = r2.json()["access_token"]

	id1 = client.get("/api/users/me", headers={"Authorization": f"Bearer {token1}"}).json()["id"]
	id2 = client.get("/api/users/me", headers={"Authorization": f"Bearer {token2}"}).json()["id"]

	return (id1, token1), (id2, token2)


def test_websocket_message(users):
	(id1, token1), (id2, token2) = users
	headers1 = {"Authorization": f"Bearer {token1}"}
	headers2 = {"Authorization": f"Bearer {token2}"}

	with client.websocket_connect(f"/api/ws/messages?token={token1}") as ws1, \
		 client.websocket_connect(f"/api/ws/messages?token={token2}") as ws2:

		msg = {"content": "hi via ws", "receiver_id": id2}
		r = client.post("/api/messages/send", json=msg, headers=headers1)
		r.json()

		assert ws2.receive_json() == r.json() == ws1.receive_json()

def test_bad_token_websocket():
	try:
		with client.websocket_connect(f"/api/ws/messages?token=BAD_TOKEN") as ws1:
			assert ws1.receive_json() == 1
	except WebSocketDisconnect as e:
		assert e.code == 4002
		assert e.reason == "Invalid token"

def test_no_token_provided_websocket():
	try:
		with client.websocket_connect(f"/api/ws/messages") as ws1:
			assert ws1.receive_json() == 1
	except WebSocketDisconnect as e:
		assert e.code == 4001
		assert e.reason == "Missing token"