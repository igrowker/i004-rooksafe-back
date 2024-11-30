from django.urls import path
from . import views

urlpatterns = [
    path('fetch-quotes/', views.fetch_quotes, name='fetch_quotes'),
    path('fetch-grahp/', views.fetch_graph_data, name='fetch_graphs_data'),
]
