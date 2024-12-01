# services/candle_generator.py
import random
from datetime import datetime, timedelta
from .finnhub_service import FinnhubService  # Assuming FinnhubService is in the same services folder

class CandleGenerator:
    
    """Helper to generate candle-like data from live quotes."""
    
    def __init__(self):
        self.finnhub_service = FinnhubService()

    def approximate_candles(self, symbol, days):
        """
        Generate approximate candlestick data for the past N days
        using live quotes (assuming periodic backend snapshots).
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            candles = []
            current_time = start_time

            # while current_time < end_time:
            #     # Fetch the live quote
            #     quote = self.finnhub_service.get_stock_quote(symbol)

            #     candle = {
            #         'time': current_time.isoformat(),
            #         'open': quote['o'],  # Open price (last known price at start of interval)
            #         'high': quote['h'],  # High price
            #         'low': quote['l'],   # Low price
            #         'close': quote['c'], # Closing price
            #     }
            #     candles.append(candle)
            

            # genera OHLC aleatorios
            while current_time < end_time:
                # Fetch the live quote
                quote = self.finnhub_service.get_stock_quote(symbol)

                open_price = round(quote['o'] * random.uniform(0.95, 1.05), 4)
                close_price = round(quote['c'] * random.uniform(0.95, 1.05), 4)
                high_price = max(open_price, close_price) * random.uniform(1.00, 1.05)
                low_price = min(open_price, close_price) * random.uniform(0.95, 1.00)

                high_price = round(high_price, 4)
                low_price = round(low_price, 4)

                candle = {
                    'time': current_time.isoformat(),
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                }
                candles.append(candle)

                # Increment time interval (e.g., hourly)
                current_time += timedelta(hours=1)

            return candles

        except Exception as e:
            raise ValueError(f"Error generating candles: {e}")
