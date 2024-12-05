
# from django.shortcuts import render
# import requests
# from datetime import datetime, timedelta
# import pytz
# from .models import PriceData  


# API_KEY = 'ct5i9t1r01qp4ur7ng1gct5i9t1r01qp4ur7ng20'

# def fetch_price_data(symbol="AAPL"):
#     url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=1&from=...&to=...&token={API_KEY}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         for i in range(len(data['t'])):
#             PriceData.objects.update_or_create(
#                 symbol=symbol,
#                 timestamp=datetime.fromtimestamp(data['t'][i], pytz.UTC),
#                 defaults={
#                     'open_price': data['o'][i],
#                     'high_price': data['h'][i],
#                     'low_price': data['l'][i],
#                     'close_price': data['c'][i],
#                     'volume': data['v'][i],
#                 }
#             )

import requests
from datetime import datetime
import pytz
from .models import PriceData
from django.conf import settings
from rest_framework.response import Response

API_KEY = 'ct5i9t1r01qp4ur7ng1gct5i9t1r01qp4ur7ng20'

# Función para obtener los símbolos desde la vista get_symbols
def get_symbols_from_api(exchange="US"):
    url = f"{settings.API_BASE_URL}/get_symbols/?exchange={exchange}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])
    else:
        return []

def fetch_price_data(symbols=None, exchange="US"):
    # Si no se pasan símbolos, obtenerlos dinámicamente
    if not symbols:
        symbols = get_symbols_from_api(exchange)

    # Iterar sobre los símbolos y obtener datos de precios para cada uno
    for symbol in symbols:
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=1&from=...&to=...&token={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for i in range(len(data['t'])):
                PriceData.objects.update_or_create(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(data['t'][i], pytz.UTC),
                    defaults={
                        'open_price': data['o'][i],
                        'high_price': data['h'][i],
                        'low_price': data['l'][i],
                        'close_price': data['c'][i],
                        'volume': data['v'][i],
                    }
                )