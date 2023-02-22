"""
Test for the ingredints API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='test@email.com', password='example@123'):
    """ Create and return user. """
    return get_user_model().objects.create(email=email, password=password)


def detail_url(ingredient_id):
    """ Return url with ingredient id. """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """ Test unautenthication API request. """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test to required auth to use retrive ingredients. """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """ Test authentication for API request. """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients(self):
        """ Test to retrive a list ingredinets. """
        Ingredient.objects.create(user=self.user, name='Chile')
        Ingredient.objects.create(user=self.user, name='Avocado')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all()
        serializers = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(res.data, serializers.data)

    def test_ingredients_limited_to_user(self):
        """ Test list of ingredients is limited to authenticated user. """
        user2 = create_user(
            email='user2@example.com',
            password='test2@123'
            )
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """ Test for update ingredient. """
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        payload = {'name': 'Pepper'}

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """ Test for delete an ingredient. """
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())
