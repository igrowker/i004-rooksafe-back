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
    # Determine the valid period and interval for yfinance
        if interval == "days":
            if amount <= 1:
                period = "1d"
            elif amount <= 5:
                period = "5d"
            elif amount <= 30:
                period = "1mo"
            elif amount <= 90:
                period = "3mo"
            elif amount <= 180:
                period = "6mo"
            elif amount <= 365:
                period = "1y"
            else:
                period = "max"
            data_interval = "1d"
        elif interval == "hours":
            period = "7d"
            data_interval = "1h"
        elif interval == "month":
            if amount == 1:
                period = "1mo"
            elif amount <= 3:
                period = "3mo"
            elif amount <= 6:
                period = "6mo"
            elif amount <= 12:
                period = "1y"
            else:
                period = "max"
            data_interval = "1mo"  # Monthly data
        else:
            raise ValueError("Invalid interval. Use 'days', 'hours', or 'month'.")

        # Fetch the stock data
        ticker = yf.Ticker(symbol)
        try:
            historical_data = ticker.history(period=period, interval=data_interval)
        except Exception as e:
            raise ValueError(f"Error fetching data: {str(e)}")

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
        {"symbol": "GOOG", "name": "Alphabet Inc. (Google)"},
        {"symbol": "AMZN", "name": "Amazon.com, Inc."},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "META", "name": "Meta Platforms Inc. (Facebook)"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust"},
        {"symbol": "NFLX", "name": "Netflix Inc."},
        {"symbol": "BA", "name": "Boeing Co."},
        {"symbol": "DIS", "name": "The Walt Disney Company"},
        {"symbol": "TSM", "name": "Taiwan Semiconductor Manufacturing Company"},
        {"symbol": "INTC", "name": "Intel Corporation"},
        {"symbol": "PYPL", "name": "PayPal Holdings, Inc."},
        {"symbol": "V", "name": "Visa Inc."},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
        {"symbol": "WMT", "name": "Walmart Inc."},
        {"symbol": "GE", "name": "General Electric Company"},
        {"symbol": "AMD", "name": "Advanced Micro Devices, Inc."},
        {"symbol": "GS", "name": "Goldman Sachs Group, Inc."},
        {"symbol": "MRK", "name": "Merck & Co., Inc."},
        {"symbol": "MCD", "name": "McDonald's Corporation"},
        {"symbol": "CVX", "name": "Chevron Corporation"},
        {"symbol": "HD", "name": "Home Depot, Inc."},
        {"symbol": "PFE", "name": "Pfizer Inc."},
        {"symbol": "KO", "name": "The Coca-Cola Company"},
        {"symbol": "XOM", "name": "Exxon Mobil Corporation"},
    ]
