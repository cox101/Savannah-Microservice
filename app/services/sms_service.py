import africastalking
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SMSService:
    def __init__(self):
        # Initialize Africa's Talking
        africastalking.initialize(
            username=settings.africas_talking_username,
            api_key=settings.africas_talking_api_key
        )
        self.sms = africastalking.SMS

    async def send_order_notification(self, phone_number: str, customer_name: str, order_item: str, order_amount: float) -> bool:
        """
        Send SMS notification when a new order is created
        """
        try:
            message = f"Hello {customer_name}! Your order for {order_item} (${order_amount:.2f}) has been received. Thank you!"
            
            # Remove any formatting from phone number and ensure it starts with +
            formatted_phone = self._format_phone_number(phone_number)
            
            if settings.africas_talking_sandbox:
                # In sandbox mode, only test numbers work
                logger.info(f"SANDBOX MODE: Would send SMS to {formatted_phone}: {message}")
                return True
            
            response = self.sms.send(message, [formatted_phone])
            
            if response['SMSMessageData']['Recipients']:
                recipient = response['SMSMessageData']['Recipients'][0]
                if recipient['status'] == 'Success':
                    logger.info(f"SMS sent successfully to {formatted_phone}")
                    return True
                else:
                    logger.error(f"Failed to send SMS: {recipient['status']}")
                    return False
            else:
                logger.error("No recipients in SMS response")
                return False
                
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False

    def _format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for Africa's Talking API
        """
        if not phone_number:
            return ""
        
        # Remove any spaces, dashes, or parentheses
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if not present (assuming Kenya +254 for demo)
        if not cleaned.startswith('254') and len(cleaned) >= 9:
            cleaned = '254' + cleaned[-9:]  # Take last 9 digits and add Kenya code
        
        return f"+{cleaned}"


# Create a singleton instance
sms_service = SMSService()