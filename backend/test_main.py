from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_echo():
    """
    A simple passing test, to be removed once I figure out how to test
    WebSockets
    """
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello"}


def test_websocket():
    with client.websocket_connect("/2") as websocket:
        data = websocket.receive_text()
        assert data == "Waiting for an opponent"
