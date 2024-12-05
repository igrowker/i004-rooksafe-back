import json
from channels.generic.websocket import AsyncWebsocketConsumer
from yfinance import stock_info  # Use yfinance or yahoo_fin for live data
import asyncio


class StockDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.symbol = self.scope['url_route']['kwargs']['symbol']
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # This method sends live stock updates
        while True:
            try:
                data = stock_info.get_live_price(self.symbol)  # Replace with yfinance live fetch if needed
                await self.send(text_data=json.dumps({
                    'symbol': self.symbol,
                    'price': round(data, 2),
                }))
                await asyncio.sleep(1)  # Fetch updates every second
            except Exception as e:
                await self.send(text_data=json.dumps({'error': str(e)}))
                break
