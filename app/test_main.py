from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_websocket():
    with client.websocket_connect("/") as websocket:
        data = websocket.receive_text()
        assert data == "Waiting for an opponent"


def test_sample_game():
    """
    Play a single game and check the received messages
    """
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
            player2.send_text("paper")

            assert {player1.receive_text() for _ in range(3)} == {
                "You played rock",
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
    TODO
    Try to connect as a third player to a game, check the message
    and make sure the connection is closed by the server

    Note: Currently blocked by
    https://github.com/aaugustin/websockets/issues/1072
    """
    assert True
