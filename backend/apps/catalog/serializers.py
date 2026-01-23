from django.conf import settings
from rest_framework import serializers

from .models import Collection, Photo, ProductVariant, Product


class AbsoluteImageField(serializers.ImageField):
    """ImageField that returns absolute URLs using BACKEND_URL setting.

    This is needed because server-side rendering from Next.js uses internal Docker
    hostnames (e.g., 'http://backend:7974') which aren't accessible from the browser.
    """

    def to_representation(self, value):
        if not value:
            return None

        # Get the relative URL
        url = value.url

        # If already absolute (e.g., S3), return as-is
        if url.startswith('http'):
            return url

        # Build absolute URL using BACKEND_URL setting
        backend_url = getattr(settings, 'BACKEND_URL', None)
        if backend_url:
            return f"{backend_url}/{url.lstrip('/')}"

        # Fallback to request-based URL building
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(url)

        return url


class ProductVariantSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    material_display = serializers.CharField(source='get_material_display', read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'size', 'material', 'material_display', 'display_name',
            'price', 'width_inches', 'height_inches', 'is_available'
        ]


class PhotoListSerializer(serializers.ModelSerializer):
    """Serializer for photo list views."""
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    collection_slug = serializers.CharField(source='collection.slug', read_only=True)
    price_range = serializers.DictField(read_only=True)
    orientation_display = serializers.CharField(source='get_orientation_display', read_only=True)
    image = AbsoluteImageField(read_only=True)
    thumbnail = AbsoluteImageField(read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'slug', 'image', 'thumbnail',
            'collection_name', 'collection_slug',
            'location', 'location_tag', 'orientation', 'orientation_display',
            'is_featured', 'price_range', 'created_at'
        ]


class PhotoDetailSerializer(serializers.ModelSerializer):
    """Serializer for photo detail view with all variants."""
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    collection_slug = serializers.CharField(source='collection.slug', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    price_range = serializers.DictField(read_only=True)
    orientation_display = serializers.CharField(source='get_orientation_display', read_only=True)
    aspect_ratio = serializers.FloatField(read_only=True)
    image = AbsoluteImageField(read_only=True)
    thumbnail = AbsoluteImageField(read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'slug', 'image', 'thumbnail', 'description',
            'collection_name', 'collection_slug',
            'location', 'location_tag', 'orientation', 'orientation_display',
            'date_taken', 'is_featured', 'price_range', 'variants', 'created_at',
            'aspect_ratio'
        ]


class CollectionListSerializer(serializers.ModelSerializer):
    """Serializer for collection list views."""
    photo_count = serializers.IntegerField(read_only=True)
    cover_image = AbsoluteImageField(read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image',
            'is_limited_edition', 'photo_count'
        ]


class CollectionDetailSerializer(serializers.ModelSerializer):
    """Serializer for collection detail view with photos."""
    # photos are prefetched in the view with is_active=True filter
    photos = PhotoListSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(read_only=True)
    cover_image = AbsoluteImageField(read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image',
            'is_limited_edition', 'photo_count', 'photos'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list views."""
    is_in_stock = serializers.BooleanField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    product_type_display = serializers.CharField(source='get_product_type_display', read_only=True)
    image = AbsoluteImageField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'product_type', 'product_type_display',
            'description', 'image', 'price', 'compare_at_price',
            'is_in_stock', 'is_on_sale', 'is_featured'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view."""
    is_in_stock = serializers.BooleanField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    product_type_display = serializers.CharField(source='get_product_type_display', read_only=True)
    image = AbsoluteImageField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'product_type', 'product_type_display',
            'description', 'long_description', 'image', 'additional_images',
            'price', 'compare_at_price', 'is_in_stock', 'is_on_sale',
            'is_featured', 'author', 'publisher', 'publication_year',
            'pages', 'dimensions', 'isbn', 'stock_quantity'
        ]
