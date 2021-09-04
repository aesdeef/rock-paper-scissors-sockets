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
