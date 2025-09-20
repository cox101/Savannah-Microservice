from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid


class Customer(models.Model):
    """
    Customer model representing a customer in the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique customer code"
    )
    name = models.CharField(max_length=255, help_text="Customer full name")
    email = models.EmailField(unique=True, help_text="Customer email address")
    
    # Phone number with validation for international format
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        help_text="Customer phone number in international format"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional relationship to Django User for authentication
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Associated user account"
    )

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        # Auto-generate customer code if not provided
        if not self.code:
            self.code = self.generate_customer_code()
        super().save(*args, **kwargs)

    def generate_customer_code(self):
        """Generate a unique customer code."""
        import random
        import string
        
        while True:
            code = 'CUST' + ''.join(random.choices(string.digits, k=6))
            if not Customer.objects.filter(code=code).exists():
                return code

    @property
    def total_orders(self):
        """Get total number of orders for this customer."""
        return self.orders.count()

    @property
    def total_spent(self):
        """Get total amount spent by this customer."""
        from django.db.models import Sum
        total = self.orders.aggregate(total=Sum('amount'))['total']
        return total or 0
