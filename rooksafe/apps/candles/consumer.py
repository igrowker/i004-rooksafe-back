from collections import defaultdict
from datetime import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TradeConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.candle_data = defaultdict(list)  # Almacena datos de trades para calcular velas.

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket desconectado: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'trade':
            await self.process_trade_data(data['data'])

    async def process_trade_data(self, trades):
        for trade in trades:
            symbol = trade['s']
            price = trade['p']
            volume = trade['v']
            timestamp = trade['t'] // 1000  # Convertir a segundos.

            # Agregar datos a la lista de trades
            self.candle_data[symbol].append({
                'price': price,
                'volume': volume,
                'timestamp': timestamp
            })

        # Generar velas cada 5 segundos
        for symbol, trades in self.candle_data.items():
            if len(trades) > 0:
                # Agrupar datos por intervalos de 5 segundos
                candles = self.generate_candles(trades)
                await self.send(json.dumps({"type": "candles", "symbol": symbol, "candles": candles}))

    def generate_candles(self, trades):
        # Agrupar datos por intervalos de 5 segundos
        grouped = defaultdict(list)
        for trade in trades:
            five_second_interval = trade['timestamp'] // 5
            grouped[five_second_interval].append(trade)

        candles = []
        for interval, group in grouped.items():
            prices = [t['price'] for t in group]
            volumes = [t['volume'] for t in group]

            # Convertir el timestamp del intervalo a un formato legible
            readable_time = datetime.fromtimestamp(interval * 5).strftime('%Y-%m-%d %H:%M:%S')

            candles.append({
                "timestamp": readable_time,  # Usar el formato legible
                "open": prices[0],
                "high": max(prices),
                "low": min(prices),
                "close": prices[-1],
                "volume": sum(volumes)
            })

        return candles