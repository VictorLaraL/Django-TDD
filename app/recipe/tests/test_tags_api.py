"""
Test for the tags API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def create_user(user='user@example.com', password='testpass123'):
    """ Create and return a new user """
    return get_user_model().objects.create_user(user, password)


class PublicTagsApiTests(TestCase):
    """ Test unauthenticated API request. """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required for retriving tags. """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """ Test authenticated API request. """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """ Test retriving a list of tags. """
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='Desert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
