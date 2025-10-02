from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from customers.models import Customer


class CustomerModelTest(TestCase):
    """Test cases for Customer model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_customer_creation(self):
        """Test creating a customer."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456',
            user=self.user
        )
        
        self.assertEqual(customer.name, 'John Doe')
        self.assertEqual(customer.email, 'john@example.com')
        self.assertEqual(customer.phone_number, '+254700123456')
        self.assertTrue(customer.code.startswith('CUST'))
        self.assertEqual(len(customer.code), 10)  # CUST + 6 digits
        
    def test_customer_auto_generate_code(self):
        """Test that customer code is auto-generated."""
        customer = Customer.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            phone_number='+254700123457'
        )
        
        self.assertIsNotNone(customer.code)
        self.assertTrue(customer.code.startswith('CUST'))
        
    def test_customer_code_uniqueness(self):
        """Test that customer codes are unique."""
        customer1 = Customer.objects.create(
            name='Customer 1',
            email='customer1@example.com',
            phone_number='+254700123456'
        )
        
        customer2 = Customer.objects.create(
            name='Customer 2',
            email='customer2@example.com',
            phone_number='+254700123457'
        )
        
        self.assertNotEqual(customer1.code, customer2.code)
        
    def test_customer_email_uniqueness(self):
        """Test that customer emails must be unique."""
        Customer.objects.create(
            name='Customer 1',
            email='same@example.com',
            phone_number='+254700123456'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            Customer.objects.create(
                name='Customer 2',
                email='same@example.com',
                phone_number='+254700123457'
            )
    
    def test_customer_str_representation(self):
        """Test customer string representation."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        expected = f"John Doe ({customer.code})"
        self.assertEqual(str(customer), expected)
        
    def test_customer_total_orders_property(self):
        """Test total_orders property."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        # Initially should be 0
        self.assertEqual(customer.total_orders, 0)
        
    def test_customer_total_spent_property(self):
        """Test total_spent property."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        # Initially should be 0
        self.assertEqual(customer.total_spent, 0)
