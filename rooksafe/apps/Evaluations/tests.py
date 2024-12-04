# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from rest_framework.test import APIClient
# from django.urls import reverse


# User = get_user_model()

# class EvaluacionViewTests(APITestCase):
#     def setUp(self):
#         # Create a test user
#         self.user = User.objects.create_user(username="testuser", password="password123")
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)
#         self.url = reverse("api/evaluations")  # Replace with the actual name of your URL route

#     def test_valid_respuestas(self):
#         data = {"respuestas": [1, 2, 3, 4]}
#         response = self.client.post(self.url, data, format="json")
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("perfil", response.data)
#         self.assertIn("nivel", response.data)
#         self.assertIn("descripción", response.data)
#         self.assertIn("puntaje", response.data)

#     def test_invalid_respuestas_missing(self):
#         data = {}
#         response = self.client.post(self.url, data, format="json")
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)

#     def test_invalid_respuestas_type(self):
#         data = {"respuestas": "not_a_list"}
#         response = self.client.post(self.url, data, format="json")
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)

#     def test_invalid_respuestas_length(self):
#         data = {"respuestas": [1, 2]}  # Fewer than expected
#         response = self.client.post(self.url, data, format="json")
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)

#     def test_invalid_respuestas_values(self):
#         data = {"respuestas": [1, 5, 3, 0]}  # Out-of-range values
#         response = self.client.post(self.url, data, format="json")
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)

#     def test_correct_user_experience_level(self):
#         data = {"respuestas": [1, 2, 3, 4]}  # Assuming this leads to a valid score
#         response = self.client.post(self.url, data, format="json")
        
#         self.user.refresh_from_db()  # Refresh user data from the database
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(self.user.experience_level, response.data.get("nivel"))

#     def test_out_of_score_range(self):
#         data = {"respuestas": [0, 0, 0, 0]}  # Responses leading to a score out of range
#         response = self.client.post(self.url, data, format="json")
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
