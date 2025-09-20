from rest_framework import serializers
from .models import Order
from customers.serializers import CustomerListSerializer


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model with customer details.
    """
    customer_details = CustomerListSerializer(source='customer', read_only=True)
    total_amount = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_details', 'item', 'amount', 'quantity',
            'total_amount', 'status', 'order_number', 'notes', 'created_at',
            'updated_at', 'sms_sent', 'sms_sent_at', 'can_be_cancelled'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at',
            'sms_sent', 'sms_sent_at'
        ]

    def validate_amount(self, value):
        """Validate that amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_quantity(self, value):
        """Validate that quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            old_status = self.instance.status
            valid_transitions = {
                'pending': ['processing', 'cancelled'],
                'processing': ['shipped', 'cancelled'],
                'shipped': ['delivered'],
                'delivered': [],  # Cannot change from delivered
                'cancelled': []   # Cannot change from cancelled
            }
            
            if value != old_status and value not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {old_status} to {value}."
                )
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new order.
    """
    class Meta:
        model = Order
        fields = ['customer', 'item', 'amount', 'quantity', 'notes']

    def validate_amount(self, value):
        """Validate that amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_quantity(self, value):
        """Validate that quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def create(self, validated_data):
        """Create order and trigger SMS notification."""
        order = Order.objects.create(**validated_data)
        
        # Trigger SMS notification asynchronously
        from .tasks import send_order_sms_notification
        send_order_sms_notification.delay(order.id)
        
        return order


class OrderListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for order list views.
    """
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'item',
            'amount', 'quantity', 'total_amount', 'status', 'created_at'
        ]


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating order status only.
    """
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            old_status = self.instance.status
            valid_transitions = {
                'pending': ['processing', 'cancelled'],
                'processing': ['shipped', 'cancelled'],
                'shipped': ['delivered'],
                'delivered': [],  # Cannot change from delivered
                'cancelled': []   # Cannot change from cancelled
            }
            
            if value != old_status and value not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {old_status} to {value}."
                )
        return value
