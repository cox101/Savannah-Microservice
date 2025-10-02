from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
from tests.conftest import AuthenticatedAPITestCase


class AuthenticationViewTest(APITestCase):
    """Test cases for authentication views."""
    
    def setUp(self):
        self.application = Application.objects.create(
            name="Test Application",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        
        user = User.objects.first()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch."""
        data = self.user_data.copy()
        data['confirm_password'] = 'differentpassword'
        
        url = reverse('register')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_user_registration_duplicate_email(self):
        """Test user registration with duplicate email."""
        # Create first user
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='password123'
        )
        
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_login(self):
        """Test user login endpoint."""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret
        }
        
        url = reverse('login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['token_type'], 'Bearer')
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword',
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret
        }
        
        url = reverse('login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_invalid_client(self):
        """Test user login with invalid client credentials."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'client_id': 'invalid_client_id',
            'client_secret': 'invalid_secret'
        }
        
        url = reverse('login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_oauth_application(self):
        """Test creating OAuth2 application."""
        url = reverse('create_app')
        data = {'name': 'My Test App'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('client_id', response.data)
        self.assertIn('client_secret', response.data)
        self.assertEqual(response.data['name'], 'My Test App')
    
    def test_health_check(self):
        """Test health check endpoint."""
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['service'], 'authentication')


class AuthenticatedViewTest(AuthenticatedAPITestCase):
    """Test cases for authenticated endpoints."""
    
    def test_user_profile_retrieve(self):
        """Test retrieving user profile."""
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
    
    def test_user_profile_update(self):
        """Test updating user profile."""
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
    
    def test_change_password(self):
        """Test changing password."""
        url = reverse('change_password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        
        # Check that access tokens are revoked
        self.assertFalse(AccessToken.objects.filter(user=self.user).exists())
    
    def test_change_password_wrong_old_password(self):
        """Test changing password with wrong old password."""
        url = reverse('change_password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_mismatch(self):
        """Test changing password with mismatched new passwords."""
        url = reverse('change_password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_info(self):
        """Test token info endpoint."""
        url = reverse('token_info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.access_token.token)
        self.assertIn('user', response.data)
    
    def test_logout(self):
        """Test logout endpoint."""
        url = reverse('logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that token is deleted
        self.assertFalse(AccessToken.objects.filter(token=self.access_token.token).exists())
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        # Remove authentication
        self.client.credentials()
        
        protected_urls = [
            reverse('profile'),
            reverse('change_password'),
            reverse('token_info'),
            reverse('logout'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
