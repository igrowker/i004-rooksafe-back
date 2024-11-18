from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, SimulationSerializer
from .models import Simulation
 

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