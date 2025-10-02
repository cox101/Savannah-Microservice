from django.test import TestCase
from decimal import Decimal
from customers.models import Customer
from orders.models import Order


class OrderModelTest(TestCase):
    """Test cases for Order model."""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
    
    def test_order_creation(self):
        """Test creating an order."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('99.99'),
            quantity=2
        )
        
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.item, 'Test Product')
        self.assertEqual(order.amount, Decimal('99.99'))
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.status, 'pending')
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith('ORD'))
    
    def test_order_auto_generate_number(self):
        """Test that order number is auto-generated."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith('ORD'))
        # Should have format: ORD + YYYYMMDD + 4 digits
        self.assertEqual(len(order.order_number), 15)
    
    def test_order_number_uniqueness(self):
        """Test that order numbers are unique."""
        order1 = Order.objects.create(
            customer=self.customer,
            item='Product 1',
            amount=Decimal('50.00')
        )
        
        order2 = Order.objects.create(
            customer=self.customer,
            item='Product 2',
            amount=Decimal('75.00')
        )
        
        self.assertNotEqual(order1.order_number, order2.order_number)
    
    def test_total_amount_property(self):
        """Test total_amount property calculation."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('25.00'),
            quantity=3
        )
        
        expected_total = Decimal('25.00') * 3
        self.assertEqual(order.total_amount, expected_total)
    
    def test_can_be_cancelled_method(self):
        """Test can_be_cancelled method."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        # Should be cancellable when pending
        self.assertTrue(order.can_be_cancelled())
        
        # Should be cancellable when processing
        order.status = 'processing'
        order.save()
        self.assertTrue(order.can_be_cancelled())
        
        # Should not be cancellable when shipped
        order.status = 'shipped'
        order.save()
        self.assertFalse(order.can_be_cancelled())
        
        # Should not be cancellable when delivered
        order.status = 'delivered'
        order.save()
        self.assertFalse(order.can_be_cancelled())
        
        # Should not be cancellable when already cancelled
        order.status = 'cancelled'
        order.save()
        self.assertFalse(order.can_be_cancelled())
    
    def test_mark_as_delivered_method(self):
        """Test mark_as_delivered method."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00'),
            status='shipped'
        )
        
        # Should successfully mark as delivered from shipped status
        result = order.mark_as_delivered()
        self.assertTrue(result)
        self.assertEqual(order.status, 'delivered')
        
        # Should not change status if not shipped
        order2 = Order.objects.create(
            customer=self.customer,
            item='Test Product 2',
            amount=Decimal('30.00'),
            status='pending'
        )
        
        result = order2.mark_as_delivered()
        self.assertFalse(result)
        self.assertEqual(order2.status, 'pending')
    
    def test_order_str_representation(self):
        """Test order string representation."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        expected = f"Order {order.order_number} - {self.customer.name}"
        self.assertEqual(str(order), expected)
    
    def test_order_default_values(self):
        """Test order default values."""
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('50.00')
        )
        
        self.assertEqual(order.quantity, 1)  # Default quantity
        self.assertEqual(order.status, 'pending')  # Default status
        self.assertFalse(order.sms_sent)  # Default SMS sent status
        self.assertIsNone(order.sms_sent_at)  # Default SMS sent timestamp
