from rest_framework import serializers

from .models import Collection, Photo, ProductVariant, Product


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

    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'slug', 'image', 'thumbnail', 'description',
            'collection_name', 'collection_slug',
            'location', 'location_tag', 'orientation', 'orientation_display',
            'date_taken', 'is_featured', 'price_range', 'variants', 'created_at'
        ]


class CollectionListSerializer(serializers.ModelSerializer):
    """Serializer for collection list views."""
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image',
            'is_limited_edition', 'photo_count'
        ]


class CollectionDetailSerializer(serializers.ModelSerializer):
    """Serializer for collection detail view with photos."""
    photos = PhotoListSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image',
            'is_limited_edition', 'photo_count', 'photos'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['photos'] = PhotoListSerializer(
            instance.photos.filter(is_active=True),
            many=True,
            context=self.context
        ).data
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list views."""
    is_in_stock = serializers.BooleanField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    product_type_display = serializers.CharField(source='get_product_type_display', read_only=True)

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

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'product_type', 'product_type_display',
            'description', 'long_description', 'image', 'additional_images',
            'price', 'compare_at_price', 'is_in_stock', 'is_on_sale',
            'is_featured', 'author', 'publisher', 'publication_year',
            'pages', 'dimensions', 'isbn', 'stock_quantity'
        ]
