import os
import sys
import django
import asyncio
import yfinance as yf
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Agrega la ruta base al sys.path
sys.path.insert(0, BASE_DIR)

# Configura las variables de entorno
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "site_app.settings.local")

# Inicializa Django
django.setup()

async def update_stock_price(stock_symbol):
    channel_layer = get_channel_layer()
    while True:
        try:
            # Obtener el precio de la acción
            stock = yf.Ticker(stock_symbol)
            stock_info = stock.history(period="1d")
            stock_price = stock_info["Close"].iloc[-1]

            # Enviar el precio al grupo del canal
            await channel_layer.group_send(
                f"stock_{stock_symbol}",
                {
                    "type": "send_stock_update",
                    "data": {
                        "symbol": stock_symbol,
                        "price": stock_price,
                    },
                }
            )

            print(f"Actualizado: {stock_symbol} -> {stock_price}")
            await asyncio.sleep(5)  # Actualizar cada 5 segundos
        except Exception as e:
            print(f"Error actualizando {stock_symbol}: {e}")
            await asyncio.sleep(5)  # Reintenta después de 5 segundos

if __name__ == "__main__":
    asyncio.run(update_stock_price("AAPL"))


