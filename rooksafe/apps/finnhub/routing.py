# routing.py
from django.urls import re_path
from .consumers import StockPriceConsumer

websocket_urlpatterns = [
    re_path(r'ws/trades/(?P<stock_symbol>\w+)/$', StockPriceConsumer.as_asgi()),
]