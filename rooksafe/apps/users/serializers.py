from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .models import Simulation

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['name'] = user.name
        token['email'] = user.email
        token['experience_level'] = user.experience_level
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add additional response data
        data.update({
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'email': self.user.email,
                'experience_level': self.user.experience_level,
            }
        })
        return data


class SimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simulation
        fields = ['investment_amount', 'asset_type']

    def validate_investment_amount(self, value):
        """Validar que el monto de inversión sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto de inversión debe ser mayor que cero.")
        return value