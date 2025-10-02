from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model with computed fields.
    """
    total_orders = serializers.ReadOnlyField()
    total_spent = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'code', 'name', 'email', 'phone_number',
            'created_at', 'updated_at', 'total_orders', 'total_spent'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def validate_email(self, value):
        """Validate that email is unique."""
        if self.instance:
            # For updates, exclude current instance
            if Customer.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A customer with this email already exists.")
        else:
            # For creation
            if Customer.objects.filter(email=value).exists():
                raise serializers.ValidationError("A customer with this email already exists.")
        return value

    def validate_phone_number(self, value):
        """Additional phone number validation."""
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code (start with +)")
        return value


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new customer.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = [
            'name', 'email', 'phone_number', 'password', 'confirm_password'
        ]

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def validate_email(self, value):
        """Validate that email is unique."""
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("A customer with this email already exists.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        """Create customer with associated user account."""
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        
        # Create user account
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data['name'].split()[0] if validated_data['name'] else '',
            last_name=' '.join(validated_data['name'].split()[1:]) if len(validated_data['name'].split()) > 1 else ''
        )
        
        # Create customer
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for customer list views.
    """
    class Meta:
        model = Customer
        fields = ['id', 'code', 'name', 'email', 'created_at']
