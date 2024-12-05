from rest_framework import serializers
from .models import EducationContent
import html
class EducationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationContent
        fields = ['id', 'title', 'content_type', 'level', 'content_url', 'created_at']


def sanitize_text(text):
    """
    Sanitizes text by escaping HTML entities and stripping unwanted whitespace.
    """
    return html.escape(text.strip())