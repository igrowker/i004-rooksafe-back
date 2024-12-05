import finnhub
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.users.models import User
from datetime import datetime, timedelta
from django.http import JsonResponse


class FinnhubService:
    
    def __init__(self):
        self.client = finnhub.Client(api_key='ct5i9t1r01qp4ur7ng1gct5i9t1r01qp4ur7ng20')


    def get_stock_quote(self, symbol):
        """Fetch the current stock quote for a given symbol."""
        try:
            return self.client.quote(symbol)
        except Exception as e:
            raise ValueError(f"Error fetching stock quote for {symbol}: {e}")


    def get_crypto_quote(self, symbol):
        """Fetch the current cryptocurrency quote for a given symbol."""
        try:
            return self.client.crypto_candles(symbol, '1', 0, 0)  # Customize as needed
        except Exception as e:
            raise ValueError(f"Error fetching crypto quote for {symbol}: {e}")

    #Premium version    
    def fetch_stock_data(self, symbol, days):
        """
        Fetch stock data from Finnhub for a given number of days.
        """
        end_time = datetime.now()  # Current time
        start_time = end_time - timedelta(days=days)  # Calculate start time based on days

        # Convert to Unix timestamps
        start_unix = int(start_time.timestamp())
        end_unix = int(end_time.timestamp())

        # Fetch historical data from Finnhub
        response = self.client.stock_candles(symbol, 'D', start_unix, end_unix)  # 'D' = Daily candles

        # Parse response
        if response['s'] != 'ok':
            raise ValueError("Error fetching data from Finnhub")

        # Prepare data for frontend
        data = [
            {'time': datetime.fromtimestamp(ts).isoformat(), 'open': o, 'high': h, 'low': l, 'close': c, 'volume': v}
            for ts, o, h, l, c, v in zip(response['t'], response['o'], response['h'], response['l'], response['c'], response['v'])
        ]

        return data


    def simulate_investment(self, symbol, user_id, initial_investment=1000):
        """
        Simulate investment based on user's experience level.
        """
        try:
            user = User.objects.get(id=user_id)
            experience_level = str(user.experience_level)
            quote = self.get_stock_quote(symbol)
            current_price = quote['c']  # Current price
            change_percent = quote['dp']  # Price change percentage
        except ValueError as e:
            raise ValueError(str(e))

        
        # Customize simulation based on experience level
        if experience_level == 'Basico':
            risk_factor = 0.5
        elif experience_level == 'Intermedio':
            risk_factor = 1.0
        else:  # advanced
            risk_factor = 1.5

        # Simulate future value
        simulated_return = initial_investment * (1 + (change_percent / 100) * risk_factor)
        return {
            'symbol': symbol,
            'current_price': current_price,
            'initial_investment': initial_investment,
            'simulated_return': round(simulated_return, 2),
            'risk_factor': risk_factor,
            'experience_level': experience_level
        }

    #Get Finnhub Symbols
    def get_stock_symbols(self, exchange="US"):
        """Fetch stock symbols for a specific exchange (e.g., US)."""
        try:
            symbols = self.client.stock_symbols(exchange)
            return [{"symbol": sym["symbol"], "name": sym["description"]} for sym in symbols[:50]] # Limitado a 50 stock
        except Exception as e:
            raise ValueError(f"Error fetching stock symbols: {e}")