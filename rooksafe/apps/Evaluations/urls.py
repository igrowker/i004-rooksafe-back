from django.urls import path
from .views import EvaluacionView

urlpatterns = [
    path('Evaluations/', EvaluacionView.as_view(), name='Evaluations'),
]
