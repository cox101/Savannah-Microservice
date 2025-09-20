from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Order(models.Model):
    """
    Order model representing a customer order.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="Customer who placed the order"
    )
    item = models.CharField(
        max_length=255,
        help_text="Description of the ordered item"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Order amount in the local currency"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the order"
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique order number"
    )
    
    # Additional order details
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of items ordered"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes for the order"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Order creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    # SMS notification tracking
    sms_sent = models.BooleanField(
        default=False,
        help_text="Whether SMS notification has been sent"
    )
    sms_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When SMS notification was sent"
    )

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        # Auto-generate order number if not provided
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate a unique order number."""
        import random
        import string
        from django.utils import timezone
        
        # Use current date + random digits
        date_part = timezone.now().strftime('%Y%m%d')
        
        while True:
            random_part = ''.join(random.choices(string.digits, k=4))
            order_number = f"ORD{date_part}{random_part}"
            if not Order.objects.filter(order_number=order_number).exists():
                return order_number

    @property
    def total_amount(self):
        """Calculate total amount (amount * quantity)."""
        return self.amount * self.quantity

    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'processing']

    def mark_as_delivered(self):
        """Mark order as delivered."""
        if self.status == 'shipped':
            self.status = 'delivered'
            self.save()
            return True
        return False
