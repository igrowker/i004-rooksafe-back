from celery import shared_task
from channels.layers import get_channel_layer
import json
import asyncio

@shared_task
def send_realtime_data():
    channel_layer = get_channel_layer()
    data = {"symbol": "AAPL", "price": 150.25}
    asyncio.run(channel_layer.group_send(
        "market_data",
        {"type": "send_market_data", "data": data}
    ))
