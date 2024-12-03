from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/trades/', consumers.TradeConsumer.as_asgi()),
]