from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationAPITestCase(TestCase):
    """Test cases for user authentication API"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.me_url = '/api/users/me/'

    def test_user_registration(self):
        """Test user can register successfully"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'staff'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_user_login(self):
        """Test user can login successfully"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='staff'
        )

        # Login
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_current_user_profile(self):
        """Test authenticated user can get their profile"""
        # Create and login user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            role='staff'
        )

        # Authenticate
        self.client.force_authenticate(user=user)

        # Get profile
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['role'], 'staff')

    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access protected endpoints"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
