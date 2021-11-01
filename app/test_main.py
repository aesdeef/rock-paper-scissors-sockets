from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_websocket():
    with client.websocket_connect("/2") as websocket:
        data = websocket.receive_text()
        assert data == "Waiting for an opponent"


def test_sample_game():
    """
    Play a single game and check the received messages
    """
    with client.websocket_connect("/2") as player1:
        assert player1.receive_text() == "Waiting for an opponent"

        with client.websocket_connect("/2") as player2:
            assert (
                player1.receive_text()
                == "Opponent found. Choose rock, paper, or scissors."
            )
            assert (
                player2.receive_text()
                == "Opponent found. Choose rock, paper, or scissors."
            )

            player1.send_text("rock")
            player2.send_text("paper")

            assert player1.receive_text() == "You played rock"
            assert player1.receive_text() == "Opponent played paper"
            assert player1.receive_text() == "You lost!"

            assert player2.receive_text() == "You played paper"
            assert player2.receive_text() == "Opponent played rock"
            assert player2.receive_text() == "You won!"
