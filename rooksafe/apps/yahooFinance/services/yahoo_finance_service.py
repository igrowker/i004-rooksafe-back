# apps/yahooFinance/services/yahoo_finance_service.py

import yfinance as yf
from datetime import datetime, timedelta

class YahooFinanceService:
    def get_stock_quote(self, symbol):
        """Fetch the current stock quote for a given symbol."""
        try:
            ticker = yf.Ticker(symbol)
            quote = ticker.history(period="1d")
            if not quote.empty:
                data = quote.iloc[-1]  # Get the latest quote
                return {
                    "symbol": symbol,
                    "date": data.name.strftime("%Y-%m-%d"),
                    "open": data["Open"],
                    "high": data["High"],
                    "low": data["Low"],
                    "close": data["Close"],
                    "volume": data["Volume"],
                }
            else:
                raise ValueError(f"No data found for symbol {symbol}")
        except Exception as e:
            raise ValueError(f"Error fetching stock quote for {symbol}: {e}")

    @staticmethod
    def get_historical_data(symbol, amount, interval):
    # Determine the period and interval based on the request
        if interval == "days":
            period = f"{amount}d"  # Example: "30d" for 30 days
            data_interval = "1d"  # Daily data
        elif interval == "hours":
            period = "1d" 
            data_interval = "1h"  # Hourly data
        else:
           raise ValueError("Invalid interval. Use 'days' or 'hours'.")
       
        # Fetch the stock data
        ticker = yf.Ticker(symbol)
        historical_data = ticker.history(period=period, interval=data_interval)
        
        if historical_data.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
    
        # Transform data to a list of dictionaries for JSON serialization
        return historical_data.reset_index().to_dict(orient="records")


    def get_stock_symbols(self, exchange="US"):
        """Yahoo Finance doesn't provide symbol lists directly, so mock this or use external resources."""
        # Return a mocked list or implement a third-party API to fetch symbols
        return [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corp."},
        ]
