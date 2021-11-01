from fastapi.testclient import TestClient

from app.main import app


def test_websocket():
    """
    Create one connection and check the message
    """
    client = TestClient(app)
    with client.websocket_connect("/") as websocket:
        assert websocket.receive_text() == "Waiting for an opponent"


def test_sample_game():
    """
    Play a single game and check the received messages
    """
    client = TestClient(app)
    with client.websocket_connect("/") as player1:
        assert player1.receive_text() == "Waiting for an opponent"

        with client.websocket_connect("/") as player2:
            assert (
                player1.receive_text()
                == "Opponent found. Choose rock, paper, or scissors."
            )
            assert (
                player2.receive_text()
                == "Opponent found. Choose rock, paper, or scissors."
            )

            player1.send_text("rock")

            assert player1.receive_text() == "You played rock"

            player2.send_text("paper")

            assert {player1.receive_text() for _ in range(2)} == {
                "Opponent played paper",
                "You lost!",
            }

            assert {player2.receive_text() for _ in range(3)} == {
                "You played paper",
                "Opponent played rock",
                "You won!",
            }


def test_cannot_move_twice():
    """
    Connect two players and try to play two moves from one connection
    """
    client = TestClient(app)
    with client.websocket_connect("/") as player1:
        player1.receive_text()

        with client.websocket_connect("/") as player2:
            player1.receive_text()
            player2.receive_text()

            player1.send_text("rock")
            assert player1.receive_text() == "You played rock"
            player1.send_text("rock")
            assert player1.receive_text() == "You have already played"


def test_accept_only_two_players():
    """
    Try to connect as a third player to a game and check the message
    """
    client = TestClient(app)
    with client.websocket_connect("/") as player1:
        player1.receive_text()
        with client.websocket_connect("/") as player2:
            player2.receive_text()
            with client.websocket_connect("/") as player3:
                assert player3.receive_text() == "Sorry, we already have two players"
