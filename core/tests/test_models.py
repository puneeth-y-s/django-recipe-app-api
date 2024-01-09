from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class ModelTests(TestCase):
    """Test models."""

    def test_create_recipe(self):
        """Test creating a recipe is successful."""

        user = get_user_model().objects.create_user(
            {
                "username": "testuser",
                "email": "testuser@gmail.com",
                "password": "password123",
            }
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description.",
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        user_details = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password123",
        }
        user = create_user(**user_details)
        tag = models.Tag.objects.create(user=user, name="tag1")
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient."""
        user_details = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password123",
        }
        user = create_user(**user_details)
        ingredient = models.Ingredient.objects.create(user=user, name="Onions")
        self.assertEqual(str(ingredient), ingredient.name)

    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")
        self.assertEqual(file_path, f"uploads\\recipe\\{uuid}.jpg")
