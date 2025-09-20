import africastalking
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """
    Service class for sending SMS notifications using Africa's Talking API.
    """
    
    def __init__(self):
        """Initialize Africa's Talking SDK."""
        self.username = settings.AFRICAS_TALKING_USERNAME
        self.api_key = settings.AFRICAS_TALKING_API_KEY
        self.sender_id = settings.AFRICAS_TALKING_SENDER_ID
        
        # Initialize Africa's Talking SDK
        africastalking.initialize(self.username, self.api_key)
        self.sms = africastalking.SMS
    
    def send_sms(self, phone_number, message):
        """
        Send SMS to a single recipient.
        
        Args:
            phone_number (str): Recipient's phone number in international format
            message (str): SMS message content
            
        Returns:
            bool: True if SMS was sent successfully, False otherwise
        """
        try:
            # Ensure phone number is in correct format
            phone_number = self._format_phone_number(phone_number)
            
            # Send SMS
            response = self.sms.send(
                message=message,
                recipients=[phone_number],
                sender_id=self.sender_id
            )
            
            # Check if SMS was sent successfully
            if response['SMSMessageData']['Recipients']:
                recipient = response['SMSMessageData']['Recipients'][0]
                if 'Success' in recipient['status']:
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return True
                else:
                    logger.error(f"Failed to send SMS to {phone_number}: {recipient['status']}")
                    return False
            else:
                logger.error(f"No recipients found in SMS response for {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending SMS to {phone_number}: {str(e)}")
            return False
    
    def send_bulk_sms(self, recipients, message):
        """
        Send SMS to multiple recipients.
        
        Args:
            recipients (list): List of phone numbers in international format
            message (str): SMS message content
            
        Returns:
            dict: Results with successful and failed sends
        """
        try:
            # Format all phone numbers
            formatted_recipients = [self._format_phone_number(phone) for phone in recipients]
            
            # Send bulk SMS
            response = self.sms.send(
                message=message,
                recipients=formatted_recipients,
                sender_id=self.sender_id
            )
            
            # Process results
            results = {
                'successful': [],
                'failed': [],
                'total_sent': 0,
                'total_failed': 0
            }
            
            if response['SMSMessageData']['Recipients']:
                for recipient in response['SMSMessageData']['Recipients']:
                    if 'Success' in recipient['status']:
                        results['successful'].append(recipient['number'])
                        results['total_sent'] += 1
                    else:
                        results['failed'].append({
                            'number': recipient['number'],
                            'status': recipient['status']
                        })
                        results['total_failed'] += 1
            
            logger.info(f"Bulk SMS sent: {results['total_sent']} successful, {results['total_failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error sending bulk SMS: {str(e)}")
            return {
                'successful': [],
                'failed': recipients,
                'total_sent': 0,
                'total_failed': len(recipients),
                'error': str(e)
            }
    
    def _format_phone_number(self, phone_number):
        """
        Format phone number to ensure it's in the correct international format.
        
        Args:
            phone_number (str): Phone number to format
            
        Returns:
            str: Formatted phone number
        """
        # Remove any spaces, hyphens, or other non-digit characters
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # If number starts with 0, assume it's a local Kenyan number
        if cleaned.startswith('0'):
            cleaned = '254' + cleaned[1:]  # Replace 0 with Kenya country code
        
        # Ensure it starts with +
        if not phone_number.startswith('+'):
            cleaned = '+' + cleaned
        else:
            cleaned = phone_number
        
        return cleaned
    
    def get_delivery_reports(self, message_id):
        """
        Get delivery reports for a sent message.
        
        Args:
            message_id (str): Message ID from the send response
            
        Returns:
            dict: Delivery report information
        """
        try:
            response = self.sms.fetch_messages()
            # Process delivery reports
            return response
        except Exception as e:
            logger.error(f"Error fetching delivery reports: {str(e)}")
            return None


# Utility functions for common SMS operations
def send_welcome_sms(customer):
    """Send welcome SMS to new customer."""
    sms_service = SMSService()
    message = f"Welcome to our service, {customer.name}! Your customer code is {customer.code}. Thank you for joining us!"
    return sms_service.send_sms(customer.phone_number, message)


def send_order_confirmation_sms(order):
    """Send order confirmation SMS."""
    sms_service = SMSService()
    message = f"Hello {order.customer.name}! Your order {order.order_number} for {order.item} (Amount: ${order.total_amount}) has been confirmed. Thank you!"
    return sms_service.send_sms(order.customer.phone_number, message)


def send_order_status_update_sms(order, old_status, new_status):
    """Send order status update SMS."""
    sms_service = SMSService()
    
    status_messages = {
        'processing': f"Your order {order.order_number} is now being processed.",
        'shipped': f"Great news! Your order {order.order_number} has been shipped and is on its way to you.",
        'delivered': f"Your order {order.order_number} has been delivered. Thank you for choosing us!",
        'cancelled': f"Your order {order.order_number} has been cancelled. If you have questions, please contact us."
    }
    
    message = status_messages.get(new_status, f"Your order {order.order_number} status has been updated to {new_status}.")
    return sms_service.send_sms(order.customer.phone_number, message)
