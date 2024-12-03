import yfinance as yf
import time
import json
import unittest


# Simulated WebSocket-like callback function
def on_message(symbol, data):
    print(f"Datos recibidos para {symbol}: {data}")

# Fetch the stock data using yfinance for a given symbol
def fetch_stock_data(symbol):
    try:
        # Fetch stock data using yfinance, changing the interval to 1d (daily data)
        stock = yf.Ticker(symbol)
        stock_data = stock.history(period="5d", interval="1d")  # Fetch the last 5 days of daily data
        if not stock_data.empty:
            last_data = stock_data.iloc[-1]  # Get the last data point
            return last_data.to_dict()
        else:
            print(f"No data available for {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# Test Case Class
class TestStockData(unittest.TestCase):  # Inherit from unittest.TestCase
    
    def test_fetch_stock_data(self):
        # Simulate subscribing to stock symbols
        symbols = ["AAPL", "BTC-USD"]
        
        for symbol in symbols:
            # Simulate a 5-second delay (to mimic "real-time" updates)
            print(f"Fetching data for {symbol}...")
            data = fetch_stock_data(symbol)
            
            if data:
                on_message(symbol, data)  # Call the callback function with the fetched data
            else:
                print(f"Failed to fetch data for {symbol}")
            
            time.sleep(5)  # Wait for 5 seconds before fetching the next stock data

if __name__ == "__main__":
    # Run the test
    unittest.main()