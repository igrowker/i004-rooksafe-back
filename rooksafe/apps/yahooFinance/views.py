from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .services.yahoo_finance_service import YahooFinanceService
from datetime import timedelta

service = YahooFinanceService()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_quotes(request):
    symbol = request.GET.get("symbol")
    if not symbol:
        return JsonResponse({"error": "Symbol is required."}, status=400)
    try:
        quote = service.get_stock_quote(symbol)
        return JsonResponse({"status": "success", "data": quote}, status=200)
    except ValueError as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_historical_data(request):
    symbol = request.GET.get("symbol")
    interval = request.GET.get("interval", "days")  # Default to "days"
    amount = int(request.GET.get("amount", 30))  # Default to 30 units (days or hours)
    
    if not symbol:
        return JsonResponse({"error": "Symbol is required."}, status=400)
    
    try:
        # Fetch historical data using the service layer
        data = service.get_historical_data(symbol, amount, interval)
        return JsonResponse({"status": "success", "data": data}, status=200)
    except ValueError as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_symbols(request):
    exchange = request.GET.get("exchange", "US")
    symbols = service.get_stock_symbols(exchange)
    return JsonResponse({"status": "success", "data": symbols}, status=200)
