import finnhub
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.users.models import User
from datetime import datetime

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

        
    def fetch_stock_data(self, symbol):
        """
        Fetch the latest stock quote for a given symbol.
        """

        try:
            # Fetch current stock quote
            response = self.client.quote(symbol)

            # Check if the response is valid
            if response.get('s') != 'ok':
                raise ValueError("Error fetching stock quote from Finnhub")

            # Extract and format the data (you can return this in any structure you prefer)
            quote_data = {
                'symbol': symbol,
                'current_price': response['c'],  # Current price
                'high': response['h'],  # High price of the day
                'low': response['l'],   # Low price of the day
                'open': response['o'],  # Open price of the day
                'previous_close': response['pc'],  # Previous close price
            }

            return quote_data

        except Exception as e:
            raise ValueError(f"Error fetching stock quote for {symbol}: {e}")


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