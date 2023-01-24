"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """ Create ad return a new user. """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ Test the public features of the user API. """

    def setUp(self):
        self.client = APIClient()
        # User data to use in all tests
        self.payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

    def test_create_user_success(self):
        """ Test creaating a user is successful. """
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.payload['email'])
        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists(self):
        """ Test error returned if user with email exists """
        # This is to create a new user
        create_user(**self.payload)
        # This is to create a new user and recibe the data
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test an error is returned if password less than 5 chars. """
        payload = self.payload
        payload['password'] = 'pw'
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Exists method return boolean to know if exist the data
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
