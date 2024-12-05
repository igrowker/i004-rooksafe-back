from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path('ws/trades', consumer.TradeConsumer.as_asgi()),
]