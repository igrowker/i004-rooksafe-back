import json
import yfinance as yf
from channels.generic.websocket import AsyncWebsocketConsumer

class StockPriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Obtener símbolo de la URL
        self.stock_symbol = self.scope['url_route']['kwargs']['stock_symbol']
        self.group_name = f"stock_{self.stock_symbol}"

        # Unir al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action', None)

        if action == "subscribe":
            # Enviar confirmación al cliente
            await self.send(json.dumps({"message": f"Subscribed to {self.stock_symbol} updates"}))

    async def send_stock_update(self, event):
        # Enviar actualización de precio al cliente
        price_data = event['data']
        await self.send(text_data=json.dumps(price_data))