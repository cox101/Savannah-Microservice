from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_order_sms_notification(order_id):
    """
    Send SMS notification to customer when an order is created.
    """
    try:
        from .models import Order
        from notifications.sms import SMSService
        
        order = Order.objects.get(id=order_id)
        
        # Prepare SMS message
        message = f"Hello {order.customer.name}! Your order {order.order_number} for {order.item} (Amount: ${order.total_amount}) has been received. Thank you for your business!"
        
        # Send SMS
        sms_service = SMSService()
        success = sms_service.send_sms(
            phone_number=order.customer.phone_number,
            message=message
        )
        
        if success:
            # Mark SMS as sent
            order.sms_sent = True
            order.sms_sent_at = timezone.now()
            order.save()
            
            logger.info(f"SMS sent successfully for order {order.order_number}")
        else:
            logger.error(f"Failed to send SMS for order {order.order_number}")
            
        return success
        
    except Order.DoesNotExist:
        logger.error(f"Order with id {order_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending SMS for order {order_id}: {str(e)}")
        return False


@shared_task
def send_order_status_update_sms(order_id, old_status, new_status):
    """
    Send SMS notification when order status changes.
    """
    try:
        from .models import Order
        from notifications.sms import SMSService
        
        order = Order.objects.get(id=order_id)
        
        # Only send SMS for important status changes
        important_statuses = ['shipped', 'delivered', 'cancelled']
        if new_status not in important_statuses:
            return True
        
        # Prepare status-specific message
        status_messages = {
            'shipped': f"Good news! Your order {order.order_number} has been shipped and is on its way to you.",
            'delivered': f"Your order {order.order_number} has been delivered. Thank you for choosing us!",
            'cancelled': f"Your order {order.order_number} has been cancelled. If you have questions, please contact us."
        }
        
        message = status_messages.get(new_status, f"Your order {order.order_number} status has been updated to {new_status}.")
        
        # Send SMS
        sms_service = SMSService()
        success = sms_service.send_sms(
            phone_number=order.customer.phone_number,
            message=message
        )
        
        if success:
            logger.info(f"Status update SMS sent for order {order.order_number}: {old_status} -> {new_status}")
        else:
            logger.error(f"Failed to send status update SMS for order {order.order_number}")
            
        return success
        
    except Order.DoesNotExist:
        logger.error(f"Order with id {order_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending status update SMS for order {order_id}: {str(e)}")
        return False
