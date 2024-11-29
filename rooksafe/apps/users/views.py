from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, SimulationSerializer , AssetSerializer
from .models import Simulation
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer, UpdateExperienceLevelSerializer
from faker import Faker
import random
from django.views.decorators.csrf import csrf_exempt


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



class StartSimulationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Inicia una nueva simulación de inversión."""
        serializer = SimulationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            simulation = serializer.save(user=request.user)
            return Response({
                "message": "Simulación creada",
                "simulation_id": simulation.id,
                "performance_data": simulation.performance_data 
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SimulationStatusView(APIView):
    permission_classes = [IsAuthenticated]  # Asegura que solo usuarios autenticados accedan a esta vista

    def get(self, request):
        """Consulta el estado de las simulaciones del usuario."""
        user_simulations = Simulation.objects.filter(user=request.user)
        simulation_data = self.get_simulation_data(user_simulations)

        return Response({"simulations": simulation_data}, status=status.HTTP_200_OK)

    def get_simulation_data(self, simulations):
        """Recopila datos de las simulaciones en formato adecuado."""
        return [
            {
                "id": sim.id,
                "investment_amount": sim.investment_amount,
                "asset_type": sim.asset_type,
                "status": sim.status,
                "performance_data": sim.performance_data,
            }
            for sim in simulations
        ]

    
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
        
#Ruta para crear Activo financiero
class CreateAsset(APIView):
    def post(self, request):
        fake = Faker()
        asset_type = random.choice(['actions', 'crypto', 'commodity', 'forex'])
        name = None
        
        if asset_type == 'actions':
            name = fake.company()
        elif asset_type == 'crypto':
            name = fake.word() + "-Coin"
        elif asset_type == 'forex' :
            name = fake.word() + "-" + fake.currency_code()
        elif asset_type == 'commodity':
            name = fake.word()

        print("name generado  " + name)
        asset_data = {
            'name': name ,
            'asset_type': asset_type,
            'current_value': fake.random_number(digits=5),
            'market_cap': fake.random_number(digits=10),
            'volume': fake.random_number(digits=8),
        }

        # Usar el serializer para crear el activo
        asset_serializer = AssetSerializer(data=asset_data)
        if asset_serializer.is_valid():
            asset = asset_serializer.save()  # Crear el activo financiero
            # Responder con un mensaje de éxito y los datos del activo creado
            return Response({
                'message': f'Activo "{name}" creado exitosamente.',
                'asset': asset_serializer.data
            }, status=status.HTTP_201_CREATED)

        # Si el serializer no es válido, responder con los errores
        return Response(asset_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WalletStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        wallet = user.wallet
        simulations = wallet.simulations.all()
        transactions = wallet.transactions.all()

        # Calculate the total current value of all simulations
        total_simulation_value = sum(
            sim.performance_data.get("current_value", 0) for sim in simulations
        )

        # Prepare wallet and simulation data
        wallet_data = {
            "balance": wallet.balance,
            "total_simulation_value": total_simulation_value,
            "total_portfolio_value": wallet.balance + total_simulation_value,
        }

        transaction_history = [
            {
                "type": txn.type,
                "amount": txn.amount,
                "created_at": txn.created_at,
            }
            for txn in transactions
        ]

        simulation_data = [
            {
                "id": sim.id,
                "investment_amount": sim.investment_amount,
                "asset_type": sim.asset_type,
                "current_value": sim.performance_data.get("current_value"),
                "status": sim.status,
            }
            for sim in simulations
        ]

        return Response({
            "wallet": wallet_data,
            "transactions": transaction_history,
            "simulations": simulation_data,
        }, status=status.HTTP_200_OK)
