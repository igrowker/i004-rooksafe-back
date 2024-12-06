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
            return JsonResponse({"error": "Wallet not found"}, status=404)
        
        # Total value of all investments
        investments = StockInvestment.objects.filter(user=request.user)
        total_investment_value = sum([investment.current_value for investment in investments])
        
        # total wallet value
        total_wallet_value = wallet.balance + total_investment_value

        # Total purchase cost for all investments
        total_purchase_costo = sum([investment.number_of_shares * investment.purchase_price for investment in investments])

        # Historical profit or loss
        total_profit_loss = total_investment_value - total_purchase_costo

        # JSON of investments
        transactions = []
        for investment in investments:
            transactions.append({
                "stock_symbol": investment.stock_symbol,
                "number_of_shares": investment.number_of_shares,
                "purchase_price": investment.purchase_price,
                "current_value": investment.current_value,
                "total_purchase_value": investment.number_of_shares * investment.purchase_price
            })

        data = {
            "balance": wallet.balance,
            "total_investment_value": total_investment_value,
            "total_wallet_value": total_wallet_value,
            "total_profit_loss": total_profit_loss,
            "investments": transactions
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
        shares = request.data.get("shares")  # Número de acciones a comprar
        stock_symbol = request.data.get("stock_symbol")  # Símbolo de la acción

        if not shares or int(shares) <= 0:
            return JsonResponse({"error": "Invalid number of shares."}, status=400)

        try:
            # Obtener el precio actual de la acción usando yfinance
            stock = yf.Ticker(stock_symbol)
            stock_info = stock.history(period="1d")
            stock_price = stock_info["Close"].iloc[-1]  # Precio de cierre más reciente

            # Calcular el costo total de la transacción
            total_cost = stock_price * int(shares)

            # Verificar si el usuario tiene suficiente saldo en su wallet
            wallet = Wallet.objects.select_for_update().get(user=request.user)
            if wallet.balance < total_cost:
                return JsonResponse({"error": "Insufficient funds."}, status=400)

            # Crear la transacción de compra y actualizar la wallet
            with db_transaction.atomic():
                wallet.balance -= total_cost
                wallet.save()

                transaction = Transaction.objects.create(
                    wallet=wallet,
                    type="buy",
                    amount=total_cost,
                    status="completed"
                )

                investment, created = StockInvestment.objects.update_or_create(
                    user=request.user,
                    stock_symbol=stock_symbol,
                    defaults={
                        'number_of_shares': int(shares),
                        'purchase_price': stock_price,
                        'current_value': stock_price * int(shares),
                    }
                )

        except Exception as e:
            return JsonResponse({"error": f"Transaction failed: {str(e)}"}, status=500)

        return JsonResponse({
            "message": "Buy transaction completed.",
            "transaction_id": transaction.id,
            "shares_purchased": int(shares),
            "stock_price": stock_price,
            "total_cost": total_cost,
            "remaining_balance": wallet.balance  
        }, status=201)


class SellTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shares = request.data.get("shares")  # Número de acciones a vender
        stock_symbol = request.data.get("stock_symbol")  # Símbolo de la acción

        # Validar el número de acciones
        if not shares or int(shares) <= 0:
            return JsonResponse({"error": "Invalid number of shares."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el precio actual de la acción usando yfinance
            stock = yf.Ticker(stock_symbol)
            stock_info = stock.history(period="1d")
            stock_price = stock_info["Close"].iloc[-1]  # Precio de cierre más reciente

            # Validar si el usuario tiene suficientes acciones
            investment = StockInvestment.objects.get(user=request.user, stock_symbol=stock_symbol)
            if investment.number_of_shares < int(shares):
                return JsonResponse({"error": "Insufficient shares to sell."}, status=status.HTTP_400_BAD_REQUEST)

            # Calcular el valor de la venta
            total_value = stock_price * int(shares)

            # Crear la transacción de venta y actualizar la wallet
            with db_transaction.atomic():
                # Reducir el número de acciones en la inversión
                investment.number_of_shares -= int(shares)
                investment.current_value = investment.number_of_shares * stock_price
                investment.save()

                # Agregar el valor total a la wallet del usuario
                wallet = Wallet.objects.select_for_update().get(user=request.user)
                wallet.balance += total_value
                wallet.save()

                # Registrar la transacción de venta
                transaction = Transaction.objects.create(
                    wallet=wallet,
                    type="sell",
                    amount=total_value,
                    status="completed"
                )

        except StockInvestment.DoesNotExist:
            return JsonResponse({"error": "No investment found for the given stock symbol."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": f"Transaction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({
            "message": "Sell transaction completed.",
            "transaction_id": transaction.id,
            "shares_sold": int(shares),
            "stock_price": stock_price,
            "total_value": total_value
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

