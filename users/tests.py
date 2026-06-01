from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):

    def setUp(self):
        self.register_client_url = '/api/auth/register/client/'
        self.register_provider_url = '/api/auth/register/provider/'
        self.login_url = '/api/auth/login/'

    def test_register_client(self):
        data = {
            'username': 'client1',
            'email': 'client1@test.com',
            'password': 'testpass123',
            'password2': 'testpass123',
        }

        response = self.client.post(self.register_client_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username='client1').role, 'client')
        self.assertNotIn('password', response.data)

    def test_register_provider(self):
        data = {
            'username': 'provider1',
            'email': 'provider1@test.com',
            'password': 'testpass123',
            'password2': 'testpass123',
        }

        response = self.client.post(self.register_provider_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username='provider1').role, 'provider')
        self.assertNotIn('password', response.data)

    def test_register_password_mismatch(self):
        data = {
            'username': 'client1',
            'email': 'client1@test.com',
            'password': 'testpass123',
            'password2': 'differentpass123',
        }

        response = self.client.post(self.register_client_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_valid_credentials(self):
        User.objects.create_user(
            username='testuser', password='testpass123', role='client'
        )

        response = self.client.post(
            self.login_url,
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(
            username='testuser', password='testpass123', role='client'
        )

        response = self.client.post(
            self.login_url,
            {'username': 'testuser', 'password': 'wrongpassword'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)