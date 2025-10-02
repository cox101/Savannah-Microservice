from django.test import TestCase
from customers.models import Customer
from customers.serializers import (
    CustomerSerializer,
    CustomerCreateSerializer,
    CustomerListSerializer
)
from django.contrib.auth.models import User


class CustomerSerializerTest(TestCase):
    """Test cases for Customer serializers."""
    
    def setUp(self):
        self.customer_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '+254700123456'
        }
        
        self.customer = Customer.objects.create(**self.customer_data)
    
    def test_customer_serializer_data(self):
        """Test CustomerSerializer serialization."""
        serializer = CustomerSerializer(self.customer)
        data = serializer.data
        
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john@example.com')
        self.assertEqual(data['phone_number'], '+254700123456')
        self.assertIn('id', data)
        self.assertIn('code', data)
        self.assertIn('created_at', data)
        self.assertIn('total_orders', data)
        self.assertIn('total_spent', data)
    
    def test_customer_serializer_validation(self):
        """Test CustomerSerializer validation."""
        serializer = CustomerSerializer(data=self.customer_data)
        self.assertTrue(serializer.is_valid())
    
    def test_customer_create_serializer_with_passwords(self):
        """Test CustomerCreateSerializer with password fields."""
        data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '+254700123457',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        
        serializer = CustomerCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        customer = serializer.save()
        self.assertEqual(customer.name, 'Jane Doe')
        self.assertIsNotNone(customer.user)
        self.assertEqual(customer.user.email, 'jane@example.com')
    
    def test_customer_create_serializer_password_mismatch(self):
        """Test CustomerCreateSerializer with password mismatch."""
        data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '+254700123457',
            'password': 'securepass123',
            'confirm_password': 'differentpass'
        }
        
        serializer = CustomerCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_customer_list_serializer(self):
        """Test CustomerListSerializer."""
        serializer = CustomerListSerializer(self.customer)
        data = serializer.data
        
        # Should only include basic fields
        expected_fields = ['id', 'code', 'name', 'email', 'created_at']
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_email_uniqueness_validation(self):
        """Test email uniqueness validation."""
        # Try to create another customer with same email
        duplicate_data = {
            'name': 'Another Customer',
            'email': 'john@example.com',  # Same email
            'phone_number': '+254700123457'
        }
        
        serializer = CustomerSerializer(data=duplicate_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_phone_number_validation(self):
        """Test phone number validation."""
        # Test without country code
        invalid_data = {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'phone_number': '0700123456'  # No + prefix
        }
        
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
