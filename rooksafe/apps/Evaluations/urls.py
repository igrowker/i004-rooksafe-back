from django.urls import path
# from .views import EvaluacionView
from .evaluationResultView import EvaluacionView

urlpatterns = [
    path('evaluations', EvaluacionView.as_view(), name='Evaluations'),
]
