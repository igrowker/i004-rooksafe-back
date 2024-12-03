from django.shortcuts import render

import requests
from datetime import datetime
from .models import PriceData


API_KEY = 'ct5i9t1r01qp4ur7ng1gct5i9t1r01qp4ur7ng20'

def fetch_price_data(symbol="AAPL"):
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=1&from=...&to=...&token={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for i in range(len(data['t'])):
            PriceData.objects.update_or_create(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(data['t'][i]),
                defaults={
                    'open_price': data['o'][i],
                    'high_price': data['h'][i],
                    'low_price': data['l'][i],
                    'close_price': data['c'][i],
                    'volume': data['v'][i],
                }
            )
