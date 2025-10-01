import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from oauth2_provider.models import Application, AccessToken
from django.utils import timezone
from datetime import timedelta
import uuid


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def oauth_application():
    """Create an OAuth2 application for testing."""
    return Application.objects.create(
        name="Test Application",
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
    )


@pytest.fixture
def access_token(user, oauth_application):
    """Create an access token for testing."""
    return AccessToken.objects.create(
        user=user,
        application=oauth_application,
        token='test-token-123',
        expires=timezone.now() + timedelta(hours=1),
        scope='read write'
    )


class AuthenticatedAPITestCase(APITestCase):
    """Base test case with authentication setup."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.application = Application.objects.create(
            name="Test Application",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        
        self.access_token = AccessToken.objects.create(
            user=self.user,
            application=self.application,
            token=str(uuid.uuid4()),
            expires=timezone.now() + timedelta(hours=1),
            scope='read write'
        )
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token.token}')
