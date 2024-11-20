from rest_framework import serializers
from .models import EducationContent

class EducationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationContent
        fields = ['id', 'title', 'content_type', 'level', 'content_url', 'created_at']
