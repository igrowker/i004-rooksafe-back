import websocket
import json

# Clave API de Finnhub
API_KEY = "ct5i9t1r01qp4ur7ng1gct5i9t1r01qp4ur7ng20"

# Función que maneja los mensajes recibidos
def on_message(ws, message):
    data = json.loads(message)
    print(f"Datos recibidos: {data}")

# Función que maneja los errores
def on_error(ws, error):
    print(f"Error: {error}")

# Función que maneja el cierre de la conexión
def on_close(ws, close_status_code, close_msg):
    print("Conexión cerrada")

# Función que maneja la apertura de la conexión
def on_open(ws):
    # Suscripción a un par de símbolos
    symbols = ["AAPL", "BTC/USD"]
    for symbol in symbols:
        subscription_message = {
            "type": "subscribe",
            "symbol": symbol
        }
        ws.send(json.dumps(subscription_message))
        print(f"Suscrito a: {symbol}")

# URL del WebSocket de Finnhub
URL = f"wss://ws.finnhub.io?token={API_KEY}"

# Configuración del WebSocket
ws = websocket.WebSocketApp(
    URL,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)

# Asignar la función on_open para cuando se establezca la conexión
ws.on_open = on_open

# Iniciar el WebSocket
ws.run_forever()