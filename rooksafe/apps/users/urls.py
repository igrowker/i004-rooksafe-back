# urls app user
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
from .views import StartSimulationView, SimulationStatusView

urlpatterns = [
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/protected/', ProtectedView.as_view(), name='protected'),
    path('api/simulator/start', StartSimulationView.as_view(), name='start_simulation'),
    path('api/simulator/status', SimulationStatusView.as_view(), name='simulation_status'),
    path('api/user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('update-experience/', UpdateExperienceLevelView.as_view(), name='update_experience_level'),
    path('asset/create/', CreateAsset.as_view(), name='create_asset'),
]