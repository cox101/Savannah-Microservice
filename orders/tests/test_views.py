from django.urls import reverse
from rest_framework import status
from decimal import Decimal
from customers.models import Customer
from orders.models import Order
from tests.conftest import AuthenticatedAPITestCase
from unittest.mock import patch


class OrderViewSetTest(AuthenticatedAPITestCase):
    """Test cases for Order ViewSet."""
    
    def setUp(self):
        super().setUp()
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        self.order_data = {
            'customer': str(self.customer.id),
            'item': 'Test Product',
            'amount': '99.99',
            'quantity': 2,
            'notes': 'Test order notes'
        }
    
    @patch('orders.tasks.send_order_sms_notification.delay')
    def test_create_order(self, mock_sms_task):
        """Test creating an order."""
        url = reverse('order-list')
        response = self.client.post(url, self.order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.item, 'Test Product')
        self.assertEqual(order.amount, Decimal('99.99'))
        self.assertEqual(order.quantity, 2)
        
        # Check that SMS task was called
        mock_sms_task.assert_called_once_with(order.id)
    
    def test_list_orders(self):
        """Test listing orders."""
        # Create test orders
        Order.objects.create(
            customer=self.customer,
            item='Product 1',
            amount=Decimal('50.00')
        )
        Order.objects.create(
            customer=self.customer,
            item='Product 2',
            amount=Decimal('75.00')
        )
        
        url = reverse('order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_order(self):
        """Test retrieving a specific order."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item'], 'Test Product')
        self.assertIn('customer_details', response.data)
    
    def test_update_order(self):
        """Test updating an order."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        url = reverse('order-detail', kwargs={'pk': order.pk})
        data = {'item': 'Updated Product'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.item, 'Updated Product')
    
    def test_update_order_status(self):
        """Test updating order status."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00'),
            status='pending'
        )
        
        url = reverse('order-update-status', kwargs={'pk': order.pk})
        data = {'status': 'processing'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'processing')
    
    def test_invalid_status_transition(self):
        """Test invalid status transition."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00'),
            status='delivered'
        )
        
        url = reverse('order-update-status', kwargs={'pk': order.pk})
        data = {'status': 'pending'}  # Can't go back from delivered
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_order(self):
        """Test cancelling an order."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00'),
            status='pending'
        )
        
        url = reverse('order-cancel', kwargs={'pk': order.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')
    
    def test_cancel_order_invalid_status(self):
        """Test cancelling an order with invalid status."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00'),
            status='delivered'
        )
        
        url = reverse('order-cancel', kwargs={'pk': order.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')  # Should remain unchanged
    
    @patch('orders.tasks.send_order_sms_notification.delay')
    def test_resend_sms(self, mock_sms_task):
        """Test resending SMS notification."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        url = reverse('order-resend-sms', kwargs={'pk': order.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_sms_task.assert_called_once_with(order.id)
    
    def test_order_analytics(self):
        """Test order analytics endpoint."""
        # Create test orders
        Order.objects.create(
            customer=self.customer,
            item='Product 1',
            amount=Decimal('50.00'),
            status='pending'
        )
        Order.objects.create(
            customer=self.customer,
            item='Product 2',
            amount=Decimal('75.00'),
            status='delivered'
        )
        
        url = reverse('order-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('orders_by_status', response.data)
        
        summary = response.data['summary']
        self.assertEqual(summary['total_orders'], 2)
        self.assertEqual(float(summary['total_revenue']), 125.00)
    
    def test_search_orders(self):
        """Test order search functionality."""
        Order.objects.create(
            customer=self.customer,
            item='Laptop Computer',
            amount=Decimal('999.99')
        )
        Order.objects.create(
            customer=self.customer,
            item='Mouse Pad',
            amount=Decimal('15.99')
        )
        
        url = reverse('order-search')
        response = self.client.get(url, {'q': 'Laptop'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['item'], 'Laptop Computer')
    
    def test_orders_by_customer(self):
        """Test getting orders by customer."""
        # Create orders for our customer
        Order.objects.create(
            customer=self.customer,
            item='Product 1',
            amount=Decimal('50.00')
        )
        Order.objects.create(
            customer=self.customer,
            item='Product 2',
            amount=Decimal('75.00')
        )
        
        # Create another customer with orders
        other_customer = Customer.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            phone_number='+254700123457'
        )
        Order.objects.create(
            customer=other_customer,
            item='Other Product',
            amount=Decimal('30.00')
        )
        
        url = reverse('order-by-customer')
        response = self.client.get(url, {'customer_id': str(self.customer.id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 2)
        self.assertEqual(float(response.data['total_spent']), 125.00)
        self.assertEqual(len(response.data['orders']), 2)
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users can't access orders."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        # Remove authentication
        self.client.credentials()
        
        # Test list endpoint
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test detail endpoint
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
