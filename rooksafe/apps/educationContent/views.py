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

        content_type = request.query_params.get('type', 'all')
        content_id = request.query_params.get('id', None)

        if content_id:
            if content_type != 'all':
                content = EducationContent.objects.filter(
                    id=content_id,
                    level=user_experience_level,
                    content_type=content_type
                )
                if content.exists():
                    serializer = EducationContentSerializer(content.first())
                    return Response({
                        "message": f"Detalles del contenido educativo con ID {content_id} para el nivel {user_experience_level}",
                        "data": serializer.data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": f"No existe contenido de tipo '{content_type}' con ID {content_id} para tu nivel de experiencia ({user_experience_level})."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "message": f"El tipo de contenido '{content_type}' no es válido o no está especificado correctamente para el ID proporcionado."
                }, status=status.HTTP_400_BAD_REQUEST)


        if content_type == 'all':
            content = EducationContent.objects.filter(level=user_experience_level)
        else:
            content = EducationContent.objects.filter(
                level=user_experience_level,
                content_type=content_type
            )
        if not content.exists():
            return Response({
                "message": f"No hay contenido educativo disponible para tu nivel de experiencia ({user_experience_level}) con los filtros especificados."
            }, status=status.HTTP_404_NOT_FOUND)



        paginator = self.CustomPagination()
        paginated_content = paginator.paginate_queryset(content, request)
        serializer = EducationContentSerializer(paginated_content, many=True)

        return paginator.get_paginated_response({
            "message": f"Contenido educativo para el nivel {user_experience_level}",
            "data": serializer.data
        })
