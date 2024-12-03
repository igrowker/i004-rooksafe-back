from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from .models import EducationContent
from .serializers import EducationContentSerializer
from django.contrib.auth import get_user_model

user = get_user_model()


class EducationContentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    class CustomPagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100

    def get(self, request):
        user = request.user
        user_experience_level = user.experience_level

        content = EducationContent.objects.filter(level=user_experience_level)

        content_type = request.query_params.get('type', None)
        if content_type:
            content = content.filter(content_type=content_type)

        if not content.exists():
            return Response({
                "message": f"No educational content available for {user_experience_level} level with the specified filters."
            }, status=status.HTTP_404_NOT_FOUND)

        paginator = self.CustomPagination()
        paginated_content = paginator.paginate_queryset(content, request)
        serializer = EducationContentSerializer(paginated_content, many=True)

        return paginator.get_paginated_response({
            "message": f"Educational content for {user_experience_level} level",
            "data": serializer.data
        })
