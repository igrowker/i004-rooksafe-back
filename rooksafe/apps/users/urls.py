# urls app user
from django.urls import path
from . import views

urlpatterns = [
    path('api/auth/register/', views.RegisterView.as_view(), name='register'),
]