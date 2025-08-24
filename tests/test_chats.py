import os

# Удаляем тестовую БД перед запуском
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_db.sqlite3")
if os.path.exists(db_path):
	try:
		os.remove(db_path)
	except OSError as e:
		print(f"Failed to remove database file: {e}")

import pytest
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)


@pytest.fixture
def user_tokens():
	u1 = {"username": "user1", "password": "pass1"}
	u2 = {"username": "user2", "password": "pass2"}

	r = client.post("/api/users/register", json=u1)
	assert r.status_code == 201
	r = client.post("/api/users/register", json=u2)
	assert r.status_code == 201

	r1 = client.post("/api/users/login", json=u1)
	r2 = client.post("/api/users/login", json=u2)
	return r1.json()["access_token"], r2.json()["access_token"]


def test_direct_message_flow(user_tokens):
	token1, token2 = user_tokens
	headers1 = {"Authorization": f"Bearer {token1}"}
	headers2 = {"Authorization": f"Bearer {token2}"}

	r = client.get("api/users/me", headers=headers1)
	assert r.status_code == 200
	results = r.json()
	user1_id = results["id"]

	r = client.get("/api/users/search", params={"username": "user2"}, headers=headers1)
	assert r.status_code == 200
	results = r.json()
	assert len(results) == 1
	user2_id = results[0]["id"]

	msg = {"content": "Hello!", "receiver_id": user2_id}
	r = client.post("/api/messages/send", json=msg, headers=headers1)
	assert r.status_code == 201
	message_data = r.json()
	assert message_data["content"] == "Hello!"
	assert message_data["sender_id"] != message_data["receiver_id"]

	r = client.get(f"/api/messages/with/{user1_id}", headers=headers2)
	assert r.status_code == 200
	messages = r.json()
	print(messages)
	assert len(messages) == 1
	assert messages[0]["content"] == "Hello!"
	assert messages[0]["sender_id"] != messages[0]["receiver_id"]