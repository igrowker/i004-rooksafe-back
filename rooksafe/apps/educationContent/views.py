from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import EducationContent
from .serializers import EducationContentSerializer

class EducationContentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user
        user_experience_level = user.experience_level

        # Filter content by the user's experience level
        content = EducationContent.objects.filter(level=user_experience_level)
        serializer = EducationContentSerializer(content, many=True)

        return Response({
            "message": f"Educational content for {user_experience_level} level",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
