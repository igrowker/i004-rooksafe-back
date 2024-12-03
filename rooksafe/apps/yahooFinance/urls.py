from django.urls import path
from . import views

urlpatterns = [
    path("quotes", views.fetch_quotes, name="fetch_quotes"),
    path("historical", views.fetch_historical_data, name="fetch_historical_data"),
    path("symbols", views.get_symbols, name="get_symbols"),
]
