from fastapi import WebSocket


class Player:
    def __init__(self, connection: WebSocket):
        self.connection = connection

    def __hash__(self):
        return self.connection.__hash__()

    async def send(self, message: str):
        await self.connection.send_text(message)

    async def receive(self) -> str:
        return await self.connection.receive_text()

    async def disconnect(self):
        await self.connection.close()
