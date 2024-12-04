from rest_framework import serializers
from .models import Evaluations


class EvaluationsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Evaluations
        fields = "__all__"

