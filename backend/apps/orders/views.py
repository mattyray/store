from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.catalog.models import ProductVariant, Product
from .models import Cart, CartItem, Order
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)


def get_or_create_cart(request):
    """Get or create a cart for the current session."""
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    # Prefetch related objects to avoid N+1 queries during serialization
    return Cart.objects.prefetch_related(
        'items__variant__photo',
        'items__product',
    ).get(pk=cart.pk)


class CartView(APIView):
    """View and manage shopping cart."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Get current cart contents."""
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    def delete(self, request):
        """Clear entire cart."""
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class CartItemView(APIView):
    """Add items to cart."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Add item to cart - supports both variants and products."""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_or_create_cart(request)
        variant_id = serializer.validated_data.get('variant_id')
        product_id = serializer.validated_data.get('product_id')
        quantity = serializer.validated_data['quantity']

        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                product=None,
                defaults={'quantity': quantity}
            )
        else:
            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=None,
                defaults={'quantity': quantity}
            )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Re-fetch with fresh prefetch cache after modification
        cart = get_or_create_cart(request)
        return Response(
            CartSerializer(cart, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class CartItemDetailView(APIView):
    """Update or delete a cart item."""
    authentication_classes = []
    permission_classes = []

    def get_cart_item(self, request, item_id):
        """Get cart item ensuring it belongs to current cart."""
        cart = get_or_create_cart(request)
        try:
            return CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return None

    def put(self, request, item_id):
        """Update cart item quantity."""
        cart_item = self.get_cart_item(request, item_id)
        if not cart_item:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()

        # Re-fetch with prefetch for serialization
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart, context={'request': request}).data)

    def delete(self, request, item_id):
        """Remove item from cart."""
        cart_item = self.get_cart_item(request, item_id)
        if not cart_item:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()

        # Re-fetch with prefetch for serialization
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart, context={'request': request}).data)


class OrderTrackingThrottle(AnonRateThrottle):
    scope = 'order_tracking'


class OrderTrackingView(APIView):
    """Look up order by order number and email for customers."""
    authentication_classes = []
    permission_classes = []
    throttle_classes = [OrderTrackingThrottle]

    def post(self, request):
        """Look up order status."""
        order_number = request.data.get('order_number', '').strip().upper()
        email = request.data.get('email', '').strip().lower()

        if not order_number or not email:
            return Response(
                {'error': 'Order number and email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(
                order_number=order_number,
                customer_email__iexact=email
            )
            return Response({
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'tracking_number': order.tracking_number or None,
                'tracking_carrier': order.tracking_carrier or None,
                'total': str(order.total),
                'created_at': order.created_at.isoformat(),
                'items': [
                    {
                        'title': item.item_title,
                        'description': item.item_description,
                        'quantity': item.quantity,
                    }
                    for item in order.items.all()
                ]
            })
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found. Please check your order number and email.'},
                status=status.HTTP_404_NOT_FOUND
            )
