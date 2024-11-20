from django.urls import path
from .views import EducationContentView

urlpatterns = [
    path('content/', EducationContentView.as_view(), name='education_content'),
]
