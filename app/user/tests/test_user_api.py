"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """ Create ad return a new user. """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ Test the public features of the user API. """

    def setUp(self):
        self.client = APIClient()
        # User data to use in all tests
        self.user_example = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

    def test_create_user_success(self):
        """ Test creaating a user is successful. """
        res = self.client.post(CREATE_USER_URL, self.user_example)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.user_example['email'])
        self.assertTrue(user.check_password(self.user_example['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists(self):
        """ Test error returned if user with email exists """
        # This is to create a new user
        create_user(**self.user_example)
        # This is to create a new user and recibe the data
        res = self.client.post(CREATE_USER_URL, self.user_example)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test an error is returned if password less than 5 chars. """
        payload = self.user_example
        payload['password'] = 'pw'
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Exists method return boolean to know if exist the data
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test generates token for valid credentials. """
        create_user(**self.user_example)

        credentials = {
            'email': self.user_example['email'],
            'password': self.user_example['password'],
        }

        res = self.client.post(TOKEN_URL, credentials)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credemtials(self):
        """
        Test returs error if credentials invalid.
        """
        create_user(**self.user_example)

        credentials = {
            'email': self.user_example['email'],
            'password': 'badpass'
            }
        res = self.client.post(TOKEN_URL, credentials)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """ Test posting a blank password returns an error. """
        credentials = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, credentials)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """ Test authentication is required for users. """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication.
    """
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """ Test retrieving profile for logged in user """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """ Test POST is not allowed for the me endpoint. """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profile for the authenticated user. """
        payload = {'name': 'update name', 'password': 'newpassword'}

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
