from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from apps.finnhub.services.finnhub_service import FinnhubService
from apps.finnhub.services.candle_generator import CandleGenerator
from django.core.cache import cache

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_quotes(request):
    """
    Fetch quotes and simulate investments based on user experience level.
    """
    symbol = request.GET.get('symbol')
    
    try:
        initial_investment = float(request.GET.get('investment', 1000))
    except ValueError:
        return JsonResponse({'error': 'Invalid investment value'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar que la inversión sea mayor a 0
    if initial_investment <= 0:
        return JsonResponse({'error': 'Investment must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the logged-in user's ID
    user = request.user  # This gives you the User instance
    user_id = user.id  # ID of the user

    service = FinnhubService()
    try:
        # Fetch simulation based on user ID
        simulation_result = service.simulate_investment(symbol, user_id, initial_investment)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'simulation': simulation_result})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_graph_data(request):
    """
    Fetch and return data for a graph based on user-specified time range.
    """
    # Get query parameters for time range
    start_time = request.GET.get('start_time')  # e.g., '2024-11-29T00:00:00'
    symbol = request.GET.get('symbol', 'AAPL')  # Default to AAPL if not provided

    if not start_time:
        return JsonResponse({'error': 'Start time is required.'}, status=400)

    # Make sure the start_time is in the correct format (e.g., ISO 8601)
    try:
        start_time = parse_datetime(start_time)  # Convert to datetime if necessary
        if not start_time:
            raise ValueError("Invalid start time format")
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use ISO 8601 (e.g., 2024-11-29T00:00:00).'}, status=400)

    # Call your service function with start_time
    try:
        finnhub_service = FinnhubService()
        data = finnhub_service.fetch_stock_data(symbol, start_time)  # end_time is automatically handled
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#Premium Version
@api_view(['GET'])
@permission_classes([IsAuthenticated])       
def get_candles(request, symbol, days):
    try:
        # Initialize FinnhubService
        finnhub_service = FinnhubService()

        # Fetch stock data
        candles = finnhub_service.fetch_stock_data(symbol, days)

        return JsonResponse({'status': 'success', 'data': candles}, status=200)
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])    
def stock_candles_api(request, symbol):
    """
    API endpoint to fetch approximate candlestick data using live quotes.
    """
    try:
        days = 1 #This int give 1 day to take the ohlc
        candle_generator = CandleGenerator()
        candles = candle_generator.approximate_candles(symbol, days)
        return JsonResponse({'status': 'success', 'data': candles}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

#Cache the response for eco fetching
def get_symbols(request):
    """API endpoint to fetch stock symbols dynamically from Finnhub."""
    try:
        exchange = request.GET.get("exchange", "US")
        cache_key = f"symbols_{exchange}"

        # Check if symbols are in cache
        symbols = cache.get(cache_key)
        if not symbols:
            service = FinnhubService()
            symbols = service.get_stock_symbols(exchange)
            cache.set(cache_key, symbols, timeout=3600)  # Cache for 1 hour

        return JsonResponse({"status": "success", "data": symbols})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)