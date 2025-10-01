from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
from oauth2_provider import views as oauth2_views
from oauth2_provider.generators import generate_client_secret
from datetime import datetime, timedelta
from django.utils import timezone
import requests
import logging
import uuid

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    TokenInfoSerializer
)

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Create a new user account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        logger.info(f"New user registered: {user.username}")
        
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint for user login with OAuth2 token generation.
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    application = serializer.validated_data['application']
    
    # Create access token
    access_token = AccessToken.objects.create(
        user=user,
        application=application,
        token=generate_client_secret(),  # Use oauth2_provider token generator
        expires=timezone.now() + timedelta(seconds=3600),  # 1 hour
        scope='read write'
    )
    
    logger.info(f"User logged in: {user.username}")
    
    return Response({
        'access_token': access_token.token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'scope': 'read write',
        'user': UserProfileSerializer(user).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout (token revocation).
    """
    try:
        # Get the token from the request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Revoke the token
            access_token = AccessToken.objects.get(token=token)
            access_token.delete()
            
            logger.info(f"User logged out: {request.user.username}")
            
            return Response({'message': 'Logout successful'})
    except AccessToken.DoesNotExist:
        pass
    
    return Response({'message': 'Logout successful'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    API endpoint for changing user password.
    """
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    # Revoke all existing tokens for security
    AccessToken.objects.filter(user=user).delete()
    
    logger.info(f"Password changed for user: {user.username}")
    
    return Response({'message': 'Password changed successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def token_info_view(request):
    """
    API endpoint for getting information about the current token.
    """
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            access_token = AccessToken.objects.get(token=token)
            
            serializer = TokenInfoSerializer(access_token)
            return Response(serializer.data)
    except AccessToken.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_oauth_application_view(request):
    """
    API endpoint for creating OAuth2 applications (for development/testing).
    This should be protected in production.
    """
    name = request.data.get('name', 'Test Application')
    
    application = Application.objects.create(
        name=name,
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
    )
    
    return Response({
        'client_id': application.client_id,
        'client_secret': application.client_secret,
        'name': application.name
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_view(request):
    """
    Health check endpoint for the authentication service.
    """
    return Response({
        'status': 'healthy',
        'service': 'authentication',
        'timestamp': datetime.now().isoformat()
    })
