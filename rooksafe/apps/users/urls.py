# urls app user
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
from .views import AddMoneyView, WalletStatusView

urlpatterns = [
    # user auth
    path('api/auth/register', RegisterView.as_view(), name='register'),
    path('api/auth/login', LoginView.as_view(), name='login'),
    path('api/auth/token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/protected', ProtectedView.as_view(), name='protected'),
    # wallet
    path('api/wallet/add_money', AddMoneyView.as_view(), name='add_money'),
    path('api/wallet/status', WalletStatusView.as_view(), name='wallet_status'),
    # user profile
    path('api/user/profile', UserProfileView.as_view(), name='user_profile'),
    path('update-experience', UpdateExperienceLevelView.as_view(), name='update_experience_level'),
    #transactions
    path('api/wallet/buy', BuyTransactionView.as_view(), name='buy_transaction'),
    path('api/wallet/sell', SellTransactionView.as_view(), name='sell_transaction'),
    path('api/wallet/withdrawal', WithdrawalTransactionView.as_view(), name='withdrawal_transaction'),
    path('api/wallet/history', SaleHistoryView.as_view(), name='withdrawal_transaction'),
    



]