from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from customers.models import Customer
from tests.conftest import AuthenticatedAPITestCase


class CustomerViewSetTest(AuthenticatedAPITestCase):
    """Test cases for Customer ViewSet."""
    
    def setUp(self):
        super().setUp()
        self.customer_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '+254700123456'
        }
    
    def test_create_customer_authenticated(self):
        """Test creating a customer when authenticated."""
        url = reverse('customer-list')
        response = self.client.post(url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        customer = Customer.objects.first()
        self.assertEqual(customer.name, 'John Doe')
        self.assertEqual(customer.email, 'john@example.com')
    
    def test_create_customer_with_user_account(self):
        """Test creating a customer with user account."""
        url = reverse('customer-list')
        data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '+254700123457',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        
        # Allow unauthenticated access for customer registration
        self.client.credentials()  # Remove authentication
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(User.objects.count(), 2)  # Original user + new user
    
    def test_list_customers(self):
        """Test listing customers."""
        # Create test customers
        Customer.objects.create(
            name='Customer 1',
            email='customer1@example.com',
            phone_number='+254700123456'
        )
        Customer.objects.create(
            name='Customer 2',
            email='customer2@example.com',
            phone_number='+254700123457'
        )
        
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_customer(self):
        """Test retrieving a specific customer."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        url = reverse('customer-detail', kwargs={'pk': customer.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')
    
    def test_update_customer(self):
        """Test updating a customer."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        url = reverse('customer-detail', kwargs={'pk': customer.pk})
        data = {'name': 'John Smith'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.name, 'John Smith')
    
    def test_delete_customer(self):
        """Test deleting a customer."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        url = reverse('customer-detail', kwargs={'pk': customer.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)
    
    def test_search_customers(self):
        """Test customer search functionality."""
        Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        Customer.objects.create(
            name='Jane Smith',
            email='jane@example.com',
            phone_number='+254700123457'
        )
        
        url = reverse('customer-search')
        response = self.client.get(url, {'q': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'John Doe')
    
    def test_customer_stats(self):
        """Test customer statistics endpoint."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        url = reverse('customer-stats', kwargs={'pk': customer.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('statistics', response.data)
        self.assertEqual(response.data['statistics']['total_orders'], 0)
    
    def test_unauthenticated_access_restricted(self):
        """Test that unauthenticated users can't access most endpoints."""
        customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        # Remove authentication
        self.client.credentials()
        
        # Test list endpoint
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test detail endpoint
        url = reverse('customer-detail', kwargs={'pk': customer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
