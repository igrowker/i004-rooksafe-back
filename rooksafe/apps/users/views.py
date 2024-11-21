from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, SimulationSerializer
from .models import Simulation
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer, UpdateExperienceLevelSerializer

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
    permission_classes = [IsAuthenticated]  # Asegura que solo usuarios autenticados accedan a esta vista

    def post(self, request):
        """Inicia una nueva simulación de inversión."""
        serializer = SimulationSerializer(data=request.data)

        if serializer.is_valid():
            # Guardar la simulación
            simulation = serializer.save(user=request.user)

            # Inicializar datos de rendimiento ficticio
            self.initialize_performance_data(simulation)

            return Response({
                "message": "Simulación creada",
                "simulation_id": simulation.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def initialize_performance_data(self, simulation):
        """Inicializa los datos de rendimiento para la simulación."""
        simulation.performance_data = {
            "initial_investment": simulation.investment_amount,
            "current_value": simulation.investment_amount,  # Inicialmente igual al monto invertido
            "fluctuations": []  # Aquí puedes añadir lógica para simular fluctuaciones
        }
        simulation.save()  # Guarda los cambios en la simulación


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

