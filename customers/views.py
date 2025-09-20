from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Customer
from .serializers import (
    CustomerSerializer,
    CustomerCreateSerializer,
    CustomerListSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers.
    
    Provides CRUD operations for customers with search and filtering capabilities.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'created_at']
    search_fields = ['name', 'email', 'code', 'phone_number']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CustomerCreateSerializer
        elif self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_permissions(self):
        """Allow unauthenticated access for customer registration."""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create customer and handle any additional logic."""
        customer = serializer.save()
        # Log customer creation
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"New customer created: {customer.code} - {customer.name}")

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get all orders for a specific customer."""
        customer = self.get_object()
        from orders.serializers import OrderSerializer
        orders = customer.orders.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search functionality."""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(code__icontains=query) |
            Q(phone_number__icontains=query)
        )

        serializer = CustomerListSerializer(customers, many=True)
        return Response({
            'count': customers.count(),
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get customer statistics."""
        customer = self.get_object()
        from django.db.models import Sum, Count, Avg
        from orders.models import Order
        
        stats = Order.objects.filter(customer=customer).aggregate(
            total_orders=Count('id'),
            total_spent=Sum('amount'),
            average_order_value=Avg('amount')
        )
        
        return Response({
            'customer': CustomerListSerializer(customer).data,
            'statistics': {
                'total_orders': stats['total_orders'] or 0,
                'total_spent': float(stats['total_spent'] or 0),
                'average_order_value': float(stats['average_order_value'] or 0),
            }
        })
