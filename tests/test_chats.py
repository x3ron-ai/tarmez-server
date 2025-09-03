import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
client = TestClient(app)


@pytest.fixture
def user_tokens():
	name1 = f"user1_{uuid.uuid4()}"
	name2 = f"user2_{uuid.uuid4()}"
	u1 = {"username": name1, "password": "pass1"}
	u2 = {"username": name2, "password": "pass2"}

	r = client.post("/api/users/register", json=u1)
	assert r.status_code == 201
	r = client.post("/api/users/register", json=u2)
	assert r.status_code == 201

	r1 = client.post("/api/users/login", json=u1)
	r2 = client.post("/api/users/login", json=u2)
	return (name1, r1.json()["access_token"]), (name2, r2.json()["access_token"])


def test_direct_message_flow(user_tokens):
	user1, user2 = user_tokens
	token1, token2 = user1[1], user2[1]
	headers1 = {"Authorization": f"Bearer {token1}"}
	headers2 = {"Authorization": f"Bearer {token2}"}

	r = client.get("api/users/me", headers=headers1)
	assert r.status_code == 200
	results = r.json()
	user1_id = results["id"]

	r = client.get("/api/users/search", params={"username": user2[0]}, headers=headers1)
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