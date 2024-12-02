from django.urls import path
from . import views

urlpatterns = [
    path('fetch-quotes', views.fetch_quotes, name='fetch_quotes'),
    path('fetch-grahp', views.fetch_graph_data, name='fetch_graphs_data'),
    #Premium Version   path('candles/<str:symbol>/<int:days>/', views.get_candles, name='stock_candles_api'),
    path('candles/<str:symbol>', views.stock_candles_api, name='stock_candles'),
    path('symbols', views.get_symbols, name='get_symbols'),
    path('simulate/<str:symbol>', views.simulate_investment, name='simulate_investment'),
]
