from django.test import TestCase
from unittest.mock import patch, MagicMock
from notifications.sms import SMSService
from customers.models import Customer
from orders.models import Order
from decimal import Decimal


class SMSServiceTest(TestCase):
    """Test cases for SMS service."""
    
    def setUp(self):
        self.sms_service = SMSService()
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone_number='+254700123456'
        )
    
    def test_format_phone_number_with_plus(self):
        """Test phone number formatting with + prefix."""
        formatted = self.sms_service._format_phone_number('+254700123456')
        self.assertEqual(formatted, '+254700123456')
    
    def test_format_phone_number_without_plus(self):
        """Test phone number formatting without + prefix."""
        formatted = self.sms_service._format_phone_number('254700123456')
        self.assertEqual(formatted, '+254700123456')
    
    def test_format_phone_number_local_kenyan(self):
        """Test phone number formatting for local Kenyan numbers."""
        formatted = self.sms_service._format_phone_number('0700123456')
        self.assertEqual(formatted, '+254700123456')
    
    def test_format_phone_number_with_spaces(self):
        """Test phone number formatting with spaces and special characters."""
        formatted = self.sms_service._format_phone_number('+254 700 123 456')
        self.assertEqual(formatted, '+254700123456')
    
    @patch('notifications.sms.africastalking.SMS.send')
    def test_send_sms_success(self, mock_send):
        """Test successful SMS sending."""
        # Mock successful response
        mock_send.return_value = {
            'SMSMessageData': {
                'Recipients': [{
                    'number': '+254700123456',
                    'status': 'Success',
                    'messageId': 'ATXid_123'
                }]
            }
        }
        
        result = self.sms_service.send_sms('+254700123456', 'Test message')
        
        self.assertTrue(result)
        mock_send.assert_called_once()
    
    @patch('notifications.sms.africastalking.SMS.send')
    def test_send_sms_failure(self, mock_send):
        """Test SMS sending failure."""
        # Mock failure response
        mock_send.return_value = {
            'SMSMessageData': {
                'Recipients': [{
                    'number': '+254700123456',
                    'status': 'Failed',
                    'messageId': None
                }]
            }
        }
        
        result = self.sms_service.send_sms('+254700123456', 'Test message')
        
        self.assertFalse(result)
    
    @patch('notifications.sms.africastalking.SMS.send')
    def test_send_sms_exception(self, mock_send):
        """Test SMS sending with exception."""
        mock_send.side_effect = Exception('API Error')
        
        result = self.sms_service.send_sms('+254700123456', 'Test message')
        
        self.assertFalse(result)
    
    @patch('notifications.sms.africastalking.SMS.send')
    def test_send_bulk_sms_success(self, mock_send):
        """Test successful bulk SMS sending."""
        recipients = ['+254700123456', '+254700123457']
        
        # Mock successful response
        mock_send.return_value = {
            'SMSMessageData': {
                'Recipients': [
                    {
                        'number': '+254700123456',
                        'status': 'Success',
                        'messageId': 'ATXid_123'
                    },
                    {
                        'number': '+254700123457',
                        'status': 'Success',
                        'messageId': 'ATXid_124'
                    }
                ]
            }
        }
        
        result = self.sms_service.send_bulk_sms(recipients, 'Test message')
        
        self.assertEqual(result['total_sent'], 2)
        self.assertEqual(result['total_failed'], 0)
        self.assertEqual(len(result['successful']), 2)
        self.assertEqual(len(result['failed']), 0)
    
    @patch('notifications.sms.africastalking.SMS.send')
    def test_send_bulk_sms_partial_failure(self, mock_send):
        """Test bulk SMS sending with partial failures."""
        recipients = ['+254700123456', '+254700123457']
        
        # Mock mixed response
        mock_send.return_value = {
            'SMSMessageData': {
                'Recipients': [
                    {
                        'number': '+254700123456',
                        'status': 'Success',
                        'messageId': 'ATXid_123'
                    },
                    {
                        'number': '+254700123457',
                        'status': 'Failed',
                        'messageId': None
                    }
                ]
            }
        }
        
        result = self.sms_service.send_bulk_sms(recipients, 'Test message')
        
        self.assertEqual(result['total_sent'], 1)
        self.assertEqual(result['total_failed'], 1)
        self.assertEqual(len(result['successful']), 1)
        self.assertEqual(len(result['failed']), 1)
    
    @patch('notifications.sms.SMSService.send_sms')
    def test_send_welcome_sms(self, mock_send_sms):
        """Test sending welcome SMS."""
        from notifications.sms import send_welcome_sms
        
        mock_send_sms.return_value = True
        
        result = send_welcome_sms(self.customer)
        
        self.assertTrue(result)
        mock_send_sms.assert_called_once()
        
        # Check that the message contains customer info
        call_args = mock_send_sms.call_args
        self.assertEqual(call_args[0][0], self.customer.phone_number)
        self.assertIn(self.customer.name, call_args[0][1])
        self.assertIn(self.customer.code, call_args[0][1])
    
    @patch('notifications.sms.SMSService.send_sms')
    def test_send_order_confirmation_sms(self, mock_send_sms):
        """Test sending order confirmation SMS."""
        from notifications.sms import send_order_confirmation_sms
        
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('99.99'),
            quantity=2
        )
        
        mock_send_sms.return_value = True
        
        result = send_order_confirmation_sms(order)
        
        self.assertTrue(result)
        mock_send_sms.assert_called_once()
        
        # Check that the message contains order info
        call_args = mock_send_sms.call_args
        self.assertEqual(call_args[0][0], self.customer.phone_number)
        message = call_args[0][1]
        self.assertIn(order.order_number, message)
        self.assertIn(order.item, message)
        self.assertIn(str(order.total_amount), message)
    
    @patch('notifications.sms.SMSService.send_sms')
    def test_send_order_status_update_sms(self, mock_send_sms):
        """Test sending order status update SMS."""
        from notifications.sms import send_order_status_update_sms
        
        order = Order.objects.create(
            customer=self.customer,
            item='Test Product',
            amount=Decimal('99.99')
        )
        
        mock_send_sms.return_value = True
        
        # Test different status updates
        test_cases = [
            ('pending', 'processing'),
            ('processing', 'shipped'),
            ('shipped', 'delivered'),
            ('processing', 'cancelled')
        ]
        
        for old_status, new_status in test_cases:
            with self.subTest(old_status=old_status, new_status=new_status):
                result = send_order_status_update_sms(order, old_status, new_status)
                self.assertTrue(result)
                
                # Check that the message contains appropriate status info
                call_args = mock_send_sms.call_args
                message = call_args[0][1]
                self.assertIn(order.order_number, message)
