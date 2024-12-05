from rest_framework import serializers
from .models import EducationContent
import html

def sanitize_text(text):
    """
    Sanitizes text by escaping HTML entities and stripping unwanted whitespace.
    """
    return html.escape(text.strip())

class EducationContentSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = EducationContent
        fields = ['id', 'title', 'content_type', 'level', 'content_url', 'image_url', 'created_at']

    def get_title(self, obj):
        return sanitize_text(obj.title)