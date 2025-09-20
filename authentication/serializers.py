from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from oauth2_provider.models import Application, AccessToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password']

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        """Create user account."""
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    client_id = serializers.CharField()
    client_secret = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate login credentials and OAuth2 client."""
        username = attrs.get('username')
        password = attrs.get('password')
        client_id = attrs.get('client_id')
        client_secret = attrs.get('client_secret')

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is deactivated.")

        # Validate OAuth2 application
        try:
            application = Application.objects.get(client_id=client_id)
            if application.client_secret != client_secret:
                raise serializers.ValidationError("Invalid client credentials.")
        except Application.DoesNotExist:
            raise serializers.ValidationError("Invalid client credentials.")

        attrs['user'] = user
        attrs['application'] = application
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate password change."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class TokenInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for access token information.
    """
    user = UserProfileSerializer(read_only=True)
    scope = serializers.CharField(source='scope_names')

    class Meta:
        model = AccessToken
        fields = ['token', 'expires', 'scope', 'user']
