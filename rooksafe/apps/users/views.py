from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, WalletSerializer
from .models import Wallet, Transaction, StockInvestment
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer, UpdateExperienceLevelSerializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import yfinance as yf
from django.db import transaction as db_transaction

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response(
                {
                    'message': 'Registro exitoso',
                    'token': access_token,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Este endpoint está protegido!'}, status=status.HTTP_200_OK)

#Handles user login and provides access tokens.
class LoginView(TokenObtainPairView):
    
    serializer_class = CustomTokenObtainPairSerializer

    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        data = request.data
        # verifica la existencia de datos
        if not data:
            return Response(
                {'message': "Formulario vacío"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserProfileSerializer(user, data=data, partial=True)
        
        if serializer.is_valid():
            # modificar la contraseña con set_password
            if 'password' in data:
                user.set_password(data['password'])
                user.save()

            serializer.save()
            return Response({'message': 'Perfil actualizado', 'updated_at': user.updated_at})

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
# Update Experience Level View
class UpdateExperienceLevelView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is logged in

    def patch(self, request):
        user = request.user  # Get the authenticated user
        serializer = UpdateExperienceLevelSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Experience level updated successfully!',
                'experience_level': serializer.data['experience_level']
            }, status=status.HTTP_200_OK)

class WalletStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)
        
        # Get the total value of all investments
        investments = StockInvestment.objects.filter(user=request.user)
        total_investment_value = sum([investment.current_value for investment in investments])
        
        # Calculate the total wallet value (balance + investments)
        total_wallet_value = wallet.balance + total_investment_value

        data = {
            "balance": wallet.balance,
            "total_investment_value": total_investment_value,
            "total_wallet_value": total_wallet_value,
        }
        
        return JsonResponse(data, status=200)


# Add money to wallet
class AddMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        
        if amount is None or float(amount) <= 0:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet = get_object_or_404(Wallet, user = request.user)
        wallet.balance += float(amount)
        wallet.save()

        return JsonResponse({'message': 'Nuevo monto añadido', 'balance' : wallet.balance}, status=status.HTTP_200_OK)


from django.db import transaction as db_transaction

class BuyTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        stock_symbol = request.data.get("stock_symbol")

        if not amount or float(amount) <= 0:
            return JsonResponse({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch stock price using yfinance
            stock = yf.Ticker(stock_symbol)
            stock_info = stock.history(period="1d")
            stock_price = stock_info["Close"].iloc[-1]

            # Calculate how many shares the user can buy
            total_stocks = float(amount) / stock_price
            total_stocks = round(total_stocks, 2)  # Round to 2 decimal places

            # Check if the user has enough funds in their wallet
            wallet = Wallet.objects.select_for_update().get(user=request.user)
            if wallet.balance < float(amount):
                return JsonResponse({"error": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

            # Create the buy transaction and update the user's wallet balance
            with db_transaction.atomic():
                # Deduct the amount from the user's wallet
                wallet.balance -= float(amount)
                wallet.save()

                # Record the transaction
                transaction = Transaction.objects.create(wallet=wallet, type="buy", amount=float(amount), status="completed")

                # Create or update stock investment record
                investment, created = StockInvestment.objects.update_or_create(
                    user=request.user, 
                    stock_symbol=stock_symbol,
                    defaults={
                        'number_of_shares': total_stocks,
                        'purchase_price': stock_price,
                        'current_value': stock_price * total_stocks,
                    }
                )

        except Exception as e:
            return JsonResponse({"error": f"Transaction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({
            "message": "Buy transaction completed.",
            "transaction_id": transaction.id,
            "stocks_purchased": total_stocks,
            "stock_price": stock_price
        }, status=status.HTTP_201_CREATED)


# class SellTransactionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         amount = request.data.get("amount")

#         if not amount or float(amount) <= 0:
#             return JsonResponse({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

#         with db_transaction.atomic():
#             wallet = Wallet.objects.select_for_update().get(user=request.user)

#             transaction = Transaction.objects.create(wallet=wallet, type="sell", amount=float(amount), status="completed")

#         return JsonResponse({"message": "Sell transaction completed.", "transaction_id": transaction.id}, status=status.HTTP_201_CREATED)


class SellTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stock_symbol = request.data.get("stock_symbol")
        shares_to_sell = request.data.get("shares_to_sell")

        if not shares_to_sell or float(shares_to_sell) <= 0:
            return JsonResponse({"error": "Invalid number of shares."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch stock price using yfinance
            stock = yf.Ticker(stock_symbol)
            stock_info = stock.history(period="1d")
            stock_price = stock_info["Close"].iloc[-1]  # Current price of the stock

            # Fetch the user's investment for the given stock
            investment = StockInvestment.objects.get(user=request.user, stock_symbol=stock_symbol)

            if investment.number_of_shares < float(shares_to_sell):
                return JsonResponse({"error": "Insufficient shares to sell."}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total sale value and profit/loss
            total_sale_value = float(shares_to_sell) * stock_price
            profit_or_loss = total_sale_value - (float(shares_to_sell) * investment.purchase_price)

            # Update the wallet balance and the investment record
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            with db_transaction.atomic():
                # Update wallet balance
                wallet.balance += total_sale_value
                wallet.save()

                # Update investment record
                investment.number_of_shares -= float(shares_to_sell)
                investment.current_value = investment.number_of_shares * stock_price
                if investment.number_of_shares == 0:
                    investment.delete()  # Remove investment if all shares are sold
                else:
                    investment.save()

                # Record the sell transaction
                transaction = Transaction.objects.create(
                    wallet=wallet,
                    type="sell",
                    amount=total_sale_value,
                    status="completed"
                )

        except StockInvestment.DoesNotExist:
            return JsonResponse({"error": "No investment found for the specified stock symbol."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": f"Transaction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({
            "message": "Sell transaction completed.",
            "transaction_id": transaction.id,
            "shares_sold": shares_to_sell,
            "sale_value": total_sale_value,
            "profit_or_loss": profit_or_loss,
            "stock_price": stock_price
        }, status=status.HTTP_201_CREATED)


class WithdrawalTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        #validation
        if not amount or float(amount) <= 0:
            return JsonResponse({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            if wallet.balance < float(amount):
                return JsonResponse({"error": "Insufficient funds for this withdrawal transaction."}, status=status.HTTP_400_BAD_REQUEST)

            transaction = Transaction.objects.create(wallet=wallet, type="withdrawal", amount=float(amount), status="completed")

        return JsonResponse({"message": "Withdrawal transaction completed.", "transaction_id": transaction.id}, status=status.HTTP_201_CREATED)
