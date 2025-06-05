from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


class AuthViewSetTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("auth-register")
        self.login_url = reverse("auth-login")
        self.refresh_url = reverse("auth-refresh")
        self.verify_url = reverse("auth-verify")
        self.logout_url = reverse("auth-logout")

        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "strongpassword123",
            "role": "tenant",
        }

        self.user = User.objects.create_user(
            email=self.user_data["email"],
            username=self.user_data["username"],
            password=self.user_data["password"],
            role=self.user_data["role"],
        )

    def test_register_user(self):
        data = {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "password": "newstrongpassword",
            "phone": "1234567890",
            "role": "tenant",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_user(self):
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post(self.refresh_url, {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_verify_token(self):
        access = str(RefreshToken.for_user(self.user).access_token)
        response = self.client.post(self.verify_url, {"token": access})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Token is valid.")

    def test_logout_user(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post(self.logout_url, {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Successfully logged out.")

    def test_logout_with_invalid_token(self):
        response = self.client.post(
            self.logout_url, {"refresh": "invalidtoken"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid token.")

    def test_logout_without_token(self):
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Refresh token required.")
