from django.urls import re_path
from .consumers import StockDataConsumer

websocket_urlpatterns = [
    re_path(r'ws/stocks/(?P<symbol>\w+)/$', StockDataConsumer.as_asgi()),
]
