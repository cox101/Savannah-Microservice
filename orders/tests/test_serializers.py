from django.test import TestCase
from decimal import Decimal
from customers.models import Customer
from orders.models import Order
from orders.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
    OrderStatusUpdateSerializer
)


class OrderSerializerTest(TestCase):
    """Test cases for Order serializers."""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
        
        self.order_data = {
            'customer': self.customer.id,
            'item': 'Test Product',
            'amount': Decimal('99.99'),
            'quantity': 2,
            'notes': 'Test notes'
        }
        
        self.order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('99.99'),
            quantity=2
        )
    
    def test_order_serializer_data(self):
        """Test OrderSerializer serialization."""
        serializer = OrderSerializer(self.order)
        data = serializer.data
        
        self.assertEqual(data['item'], 'Test Product')
        self.assertEqual(Decimal(data['amount']), Decimal('99.99'))
        self.assertEqual(data['quantity'], 2)
        self.assertIn('id', data)
        self.assertIn('order_number', data)
        self.assertIn('customer_details', data)
        self.assertIn('total_amount', data)
        self.assertIn('can_be_cancelled', data)
    
    def test_order_create_serializer(self):
        """Test OrderCreateSerializer."""
        serializer = OrderCreateSerializer(data=self.order_data)
        self.assertTrue(serializer.is_valid())
        
        # Note: We can't test the actual creation here because it triggers
        # Celery tasks which would fail in testing environment
    
    def test_order_serializer_validation_positive_amount(self):
        """Test that amount must be positive."""
        invalid_data = self.order_data.copy()
        invalid_data['amount'] = Decimal('-10.00')
        
        serializer = OrderCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
    
    def test_order_serializer_validation_positive_quantity(self):
        """Test that quantity must be positive."""
        invalid_data = self.order_data.copy()
        invalid_data['quantity'] = 0
        
        serializer = OrderCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)
    
    def test_order_status_update_serializer(self):
        """Test OrderStatusUpdateSerializer."""
        # Valid status transition
        serializer = OrderStatusUpdateSerializer(
            self.order,
            data={'status': 'processing'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        
        # Invalid status transition
        self.order.status = 'delivered'
        self.order.save()
        
        serializer = OrderStatusUpdateSerializer(
            self.order,
            data={'status': 'pending'},
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
    
    def test_order_list_serializer(self):
        """Test OrderListSerializer."""
        serializer = OrderListSerializer(self.order)
        data = serializer.data
        
        # Should include simplified fields
        expected_fields = [
            'id', 'order_number', 'customer_name', 'item',
            'amount', 'quantity', 'total_amount', 'status', 'created_at'
        ]
        self.assertEqual(set(data.keys()), set(expected_fields))
        self.assertEqual(data['customer_name'], self.customer.name)
    
    def test_order_serializer_readonly_fields(self):
        """Test that certain fields are read-only."""
        serializer = OrderSerializer(self.order)
        
        # These fields should be read-only
        readonly_fields = ['id', 'order_number', 'created_at', 'updated_at', 'sms_sent', 'sms_sent_at']
        
        for field in readonly_fields:
            self.assertTrue(serializer.fields[field].read_only)
    
    def test_valid_status_transitions(self):
        """Test all valid status transitions."""
        # Test pending -> processing
        self.order.status = 'pending'
        self.order.save()
        
        serializer = OrderStatusUpdateSerializer(
            self.order,
            data={'status': 'processing'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        
        # Test processing -> shipped
        self.order.status = 'processing'
        self.order.save()
        
        serializer = OrderStatusUpdateSerializer(
            self.order,
            data={'status': 'shipped'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        
        # Test shipped -> delivered
        self.order.status = 'shipped'
        self.order.save()
        
        serializer = OrderStatusUpdateSerializer(
            self.order,
            data={'status': 'delivered'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_status_transitions(self):
        """Test invalid status transitions."""
        # Test delivered -> any other status
        self.order.status = 'delivered'
        self.order.save()
        
        for invalid_status in ['pending', 'processing', 'shipped', 'cancelled']:
            serializer = OrderStatusUpdateSerializer(
                self.order,
                data={'status': invalid_status},
                partial=True
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn('status', serializer.errors)
