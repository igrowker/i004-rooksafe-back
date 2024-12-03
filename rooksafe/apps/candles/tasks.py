from channels.layers import get_channel_layer
import asyncio
import json

async def send_realtime_data():
    channel_layer = get_channel_layer()
    while True:
        # Simulación de datos (sustituye con datos reales)
        data = {"symbol": "AAPL", "price": 150.25}
        await channel_layer.group_send(
            "market_data",
            {"type": "send_market_data", "data": data}
        )
        await asyncio.sleep(1)  # Ajusta la frecuencia según lo necesario