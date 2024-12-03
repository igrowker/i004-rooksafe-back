from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, WalletSerializer
from .models import Wallet, Transaction
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer, UpdateExperienceLevelSerializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

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
            return JsonResponse({"error":"Not found"}, status=404)
        
        serializer = WalletSerializer(wallet)
        return JsonResponse(serializer.data, status=200)



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

        if not amount or float(amount) <= 0:
            return JsonResponse({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            if wallet.balance < float(amount):
                return JsonResponse({"error": "Insufficient funds for this buy transaction."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                transaction = Transaction.objects.create(wallet=wallet, type="buy", amount=float(amount), status="completed")
            except Exception as e:
                return JsonResponse({"error": f"Transaction creation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({"message": "Buy transaction completed.", "transaction_id": transaction.id}, status=status.HTTP_201_CREATED)


class SellTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")

        if not amount or float(amount) <= 0:
            return JsonResponse({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            transaction = Transaction.objects.create(wallet=wallet, type="sell", amount=float(amount), status="completed")

        return JsonResponse({"message": "Sell transaction completed.", "transaction_id": transaction.id}, status=status.HTTP_201_CREATED)


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
