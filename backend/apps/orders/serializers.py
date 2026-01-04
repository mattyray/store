from rest_framework import serializers

from apps.catalog.models import ProductVariant, Product
from apps.catalog.serializers import ProductVariantSerializer, ProductListSerializer
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items - handles both variants and products."""
    variant = ProductVariantSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    item_type = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    image = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'item_type', 'variant', 'product', 'quantity',
            'title', 'description', 'slug', 'image', 'unit_price', 'total_price'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.variant and obj.variant.photo.thumbnail:
            return request.build_absolute_uri(obj.variant.photo.thumbnail.url) if request else obj.variant.photo.thumbnail.url
        elif obj.variant and obj.variant.photo.image:
            return request.build_absolute_uri(obj.variant.photo.image.url) if request else obj.variant.photo.image.url
        elif obj.product and obj.product.image:
            return request.build_absolute_uri(obj.product.image.url) if request else obj.product.image.url
        return None

    def get_slug(self, obj):
        if obj.variant:
            return obj.variant.photo.slug
        elif obj.product:
            return obj.product.slug
        return None


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart."""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart - handles both variants and products."""
    variant_id = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        variant_id = data.get('variant_id')
        product_id = data.get('product_id')

        if not variant_id and not product_id:
            raise serializers.ValidationError("Either variant_id or product_id is required.")
        if variant_id and product_id:
            raise serializers.ValidationError("Provide either variant_id or product_id, not both.")

        if variant_id:
            try:
                ProductVariant.objects.get(id=variant_id, is_available=True)
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError({"variant_id": "Product variant not found or unavailable."})

        if product_id:
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                if product.track_inventory and product.stock_quantity < data.get('quantity', 1):
                    raise serializers.ValidationError({"product_id": "Not enough stock available."})
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product_id": "Product not found or unavailable."})

        return data


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    item_type = serializers.CharField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'item_type', 'item_title', 'item_description',
            'quantity', 'unit_price', 'total_price'
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_email', 'customer_name',
            'shipping_address', 'status', 'status_display',
            'subtotal', 'shipping_cost', 'tax', 'total',
            'items', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']
