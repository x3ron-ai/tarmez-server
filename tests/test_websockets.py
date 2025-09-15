import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from starlette.websockets import WebSocketDisconnect

client = TestClient(app)


@pytest.fixture
def users():
    u1 = {"username": f"ws_user1_{uuid.uuid4()}", "password": "password1"}
    u2 = {"username": f"ws_user2_{uuid.uuid4()}", "password": "password2"}

    assert client.post("/api/users/register", json=u1).status_code == 201
    assert client.post("/api/users/register", json=u2).status_code == 201

    r1 = client.post("/api/users/login", json=u1)
    r2 = client.post("/api/users/login", json=u2)
    token1 = r1.json()["access_token"]
    token2 = r2.json()["access_token"]

    id1 = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token1}"}
    ).json()["id"]
    id2 = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token2}"}
    ).json()["id"]

    return (id1, token1), (id2, token2)


def test_websocket_message(users):
    (id1, token1), (id2, token2) = users

    with client.websocket_connect(
        f"/api/ws/messages?token={token1}"
    ) as ws1, client.websocket_connect(f"/api/ws/messages?token={token2}") as ws2:

        msg = {"content": "hi via ws", "receiver_id": id2}
        r = client.post(
            "/api/messages/send",
            json=msg,
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert r.status_code == 201
        sent_msg = r.json()

        recv2 = ws2.receive_json()
        recv1 = ws1.receive_json()

        assert recv1 == recv2 == sent_msg


def test_multiple_sessions_receive(users):
    (id1, token1), (id2, token2) = users

    with client.websocket_connect(
        f"/api/ws/messages?token={token2}"
    ) as ws2a, client.websocket_connect(
        f"/api/ws/messages?token={token2}"
    ) as ws2b, client.websocket_connect(
        f"/api/ws/messages?token={token1}"
    ) as ws1:

        msg = {"content": "multisession test", "receiver_id": id2}
        r = client.post(
            "/api/messages/send",
            json=msg,
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert r.status_code == 201
        sent_msg = r.json()

        recv2a = ws2a.receive_json()
        recv2b = ws2b.receive_json()
        recv1 = ws1.receive_json()

        assert recv2a == recv2b == recv1 == sent_msg


def test_bad_token_websocket():
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect(f"/api/ws/messages?token=BAD_TOKEN"):
            pass
    assert e.value.code == 4002
    assert e.value.reason == "Invalid token"


def test_no_token_provided_websocket():
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect(f"/api/ws/messages"):
            pass
    assert e.value.code == 4001
    assert e.value.reason == "Missing token"
