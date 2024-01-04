"""
Test for the user API
"""
from django import setup
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipe_app_api.settings")
setup()

from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


# Unauthenticated tests


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""

        payload = {
            "username": "TestUser",
            "email": "testuser@gmail.com",
            "password": "Testing@123",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error returns if user with email exists"""

        payload = {
            "email": "test@gmail.com",
            "username": "TestUser",
            "password": "password123",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""

        payload = {
            "email": "test@gmail.com",
            "username": "TestUser",
            "password": "pass",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            "email": "test@gmail.com",
            "username": "TestUser",
            "password": "password123",
        }
        create_user(**user_details)

        payload = {
            "username": user_details["username"],
            "password": user_details["password"],
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""

        create_user(username="testuser", password="goodpass")

        payload = {
            "username": "testuser",
            "password": "badpass",
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error"""

        payload = {"username": "testuser", "password": ""}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Authenticated tests


class PrivateUserApiTests(TestCase):
    """Test api requests that requires authentication"""

    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            username="testuser",
            password="Testing@123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "email": self.user.email,
                "username": self.user.username,
            },
        )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {
            "username": "testuser_updated",
            "password": "Testing@123",
        }
        res = self.client.patch(ME_URL, payload)

        # to get updated data from the user table
        self.user.refresh_from_db()

        self.assertEqual(self.user.username, payload["username"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
