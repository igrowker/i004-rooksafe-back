from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import EducationContent

class EducationContentViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass", experience_level="beginner"
        )
        self.client.force_authenticate(user=self.user)

        # Add test data
        EducationContent.objects.create(id=1, level="beginner", content_type="article", title="Test Article")

    def test_get_all_content(self):
        response = self.client.get("/api/education-content/?type=all")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_content_by_type_and_id(self):
        response = self.client.get("/api/education-content/?type=article&id=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_type_with_id(self):
        response = self.client.get("/api/education-content/?type=invalid&id=1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
