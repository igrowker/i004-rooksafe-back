import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import websocket

class TradeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Iniciar conexión WebSocket a Finnhub
        self.finnhub_ws = websocket.WebSocketApp(
            "wss://ws.finnhub.io?token=ct5i9t1r01qp4ur7ng1gct5i9t1r01qp4ur7ng20",
            on_message=self.on_finnhub_message,
            on_error=self.on_finnhub_error,
            on_close=self.on_finnhub_close,
        )

        # Ejecutar la conexión WebSocket en un hilo separado
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.finnhub_ws.run_forever)

    async def disconnect(self, close_code):
        self.finnhub_ws.close()

    async def on_finnhub_message(self, message):
        # Enviar datos al frontend
        await self.send(text_data=json.dumps({"type": "trade_update", "data": json.loads(message)}))

    async def on_finnhub_error(self, error):
        await self.send(text_data=json.dumps({"type": "error", "message": str(error)}))

    async def on_finnhub_close(self):
        await self.send(text_data=json.dumps({"type": "info", "message": "Conexión cerrada con Finnhub"}))