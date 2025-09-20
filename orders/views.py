from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
    OrderStatusUpdateSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    
    Provides CRUD operations for orders with search, filtering, and analytics.
    """
    queryset = Order.objects.select_related('customer').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer', 'created_at']
    search_fields = ['item', 'order_number', 'customer__name', 'customer__email']
    ordering_fields = ['created_at', 'updated_at', 'amount', 'order_number']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'list':
            return OrderListSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        """Create order and handle additional logic."""
        order = serializer.save()
        # Log order creation
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"New order created: {order.order_number} for customer {order.customer.name}")

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update order status with validation."""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Log status change
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Order {order.order_number} status updated to {order.status}")
            
            return Response(OrderSerializer(order).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order if possible."""
        order = self.get_object()
        
        if not order.can_be_cancelled():
            return Response(
                {'error': f'Cannot cancel order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'message': f'Order {order.order_number} has been cancelled',
            'order': OrderSerializer(order).data
        })

    @action(detail=True, methods=['post'])
    def resend_sms(self, request, pk=None):
        """Resend SMS notification for an order."""
        order = self.get_object()
        
        # Trigger SMS notification
        from .tasks import send_order_sms_notification
        send_order_sms_notification.delay(order.id)
        
        return Response({
            'message': f'SMS notification queued for order {order.order_number}'
        })

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get order analytics and statistics."""
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Calculate statistics
        total_orders = queryset.count()
        total_revenue = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Orders by status
        status_counts = {}
        for status_choice in Order.STATUS_CHOICES:
            status_key = status_choice[0]
            status_counts[status_key] = queryset.filter(status=status_key).count()

        # Recent orders (last 7 days)
        week_ago = timezone.now() - timezone.timedelta(days=7)
        recent_orders = queryset.filter(created_at__gte=week_ago).count()

        # Average order value
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'average_order_value': float(avg_order_value),
                'recent_orders_7_days': recent_orders
            },
            'orders_by_status': status_counts
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search functionality."""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        orders = self.get_queryset().filter(
            Q(item__icontains=query) |
            Q(order_number__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(customer__email__icontains=query) |
            Q(notes__icontains=query)
        )

        serializer = OrderListSerializer(orders, many=True)
        return Response({
            'count': orders.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """Get orders grouped by customer."""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        orders = self.get_queryset().filter(customer_id=customer_id)
        serializer = OrderListSerializer(orders, many=True)
        
        # Calculate customer statistics
        total_spent = orders.aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'customer_id': customer_id,
            'total_orders': orders.count(),
            'total_spent': float(total_spent),
            'orders': serializer.data
        })
