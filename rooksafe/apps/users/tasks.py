from celery import shared_task
import yfinance as yf
from .models import StockInvestment

@shared_task
def update_stock_values():
    investments = StockInvestment.objects.all()

    for investment in investments:
        stock = yf.Ticker(investment.stock_symbol)
        stock_info = stock.history(period="1d")
        stock_price = stock_info["Close"].iloc[-1]
        
        # Update the current value of the investment
        investment.current_value = stock_price * investment.number_of_shares
        investment.save()
