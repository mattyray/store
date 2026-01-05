# Photography Store - Project Export

Django + Next.js e-commerce store for fine art photography prints.

**Stack:** Django 5 + DRF (backend), Next.js 16 + Tailwind (frontend), PostgreSQL, Stripe, Docker

## Project Structure

```
store/
├── docker-compose.yml
├── backend/
│   ├── .env.example
│   ├── Dockerfile
│   ├── apps/catalog/admin.py
│   ├── apps/catalog/models.py
│   ├── apps/catalog/serializers.py
│   ├── apps/catalog/urls.py
│   ├── apps/catalog/views.py
│   ├── apps/core/admin.py
│   ├── apps/core/models.py
│   ├── apps/core/urls.py
│   ├── apps/core/views.py
│   ├── apps/orders/admin.py
│   ├── apps/orders/emails.py
│   ├── apps/orders/models.py
│   ├── apps/orders/serializers.py
│   ├── apps/orders/urls.py
│   ├── apps/orders/views.py
│   ├── apps/payments/urls.py
│   ├── apps/payments/views.py
│   ├── config/settings/base.py
│   ├── config/settings/development.py
│   ├── config/settings/production.py
│   ├── config/urls.py
│   ├── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── package.json
│   ├── src/app/about/page.tsx
│   ├── src/app/book/[slug]/page.tsx
│   ├── src/app/book/page.tsx
│   ├── src/app/cart/page.tsx
│   ├── src/app/collections/[slug]/page.tsx
│   ├── src/app/collections/page.tsx
│   ├── src/app/contact/page.tsx
│   ├── src/app/gift-cards/page.tsx
│   ├── src/app/layout.tsx
│   ├── src/app/order/success/page.tsx
│   ├── src/app/page.tsx
│   ├── src/app/photos/[slug]/page.tsx
│   ├── src/app/photos/page.tsx
│   ├── src/app/track-order/page.tsx
│   ├── src/components/Footer.tsx
│   ├── src/components/Header.tsx
│   ├── src/components/PhotoCard.tsx
│   ├── src/lib/api.ts
│   ├── src/types/index.ts
```

---

## Source Files

### backend/apps/catalog/models.py

```python
from django.db import models
from django.utils.text import slugify


class Collection(models.Model):
    """A collection/series of photographs."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='collections/', blank=True)
    is_limited_edition = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def photo_count(self):
        return self.photos.filter(is_active=True).count()


class Photo(models.Model):
    """An individual photograph available for purchase."""

    ORIENTATION_CHOICES = [
        ('H', 'Horizontal'),
        ('V', 'Vertical'),
        ('S', 'Square'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    image = models.ImageField(upload_to='photos/')
    thumbnail = models.ImageField(upload_to='photos/thumbnails/', blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    location_tag = models.CharField(
        max_length=100,
        blank=True,
        help_text='Lowercase tag for filtering (e.g., montauk, east-hampton)'
    )
    orientation = models.CharField(
        max_length=1,
        choices=ORIENTATION_CHOICES,
        default='H'
    )
    date_taken = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def price_range(self):
        """Returns the price range for this photo's variants."""
        variants = self.variants.filter(is_available=True)
        if not variants.exists():
            return None
        prices = variants.values_list('price', flat=True)
        return {'min': min(prices), 'max': max(prices)}


class ProductVariant(models.Model):
    """A purchasable variant of a photo (size + material combination)."""

    MATERIAL_CHOICES = [
        ('paper', 'Paper Print'),
        ('aluminum', 'Aluminum Print'),
    ]

    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    size = models.CharField(max_length=20, help_text='e.g., 16x24, 20x30')
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    width_inches = models.PositiveIntegerField()
    height_inches = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    aluminyze_sku = models.CharField(
        max_length=100,
        blank=True,
        help_text='SKU for Aluminyze fulfillment (aluminum prints only)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['material', 'price']
        unique_together = ['photo', 'size', 'material']

    def __str__(self):
        return f"{self.photo.title} - {self.size} {self.get_material_display()}"

    @property
    def display_name(self):
        return f'{self.size}" {self.get_material_display()}'


class Product(models.Model):
    """A standalone product like a book or merchandise."""

    PRODUCT_TYPE_CHOICES = [
        ('book', 'Book'),
        ('merch', 'Merchandise'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='book')
    description = models.TextField(blank=True)
    long_description = models.TextField(blank=True, help_text='Detailed description for product page')
    image = models.ImageField(upload_to='products/')
    additional_images = models.JSONField(default=list, blank=True, help_text='List of additional image URLs')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Original price for showing discounts'
    )
    sku = models.CharField(max_length=100, blank=True)
    weight_oz = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Book-specific fields
    author = models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True, help_text='e.g., 12" x 10"')
    isbn = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0

    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.price
```

### backend/apps/catalog/views.py

```python
from django.db import models
from django.db.models import Min
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from .models import Collection, Photo, Product
from .serializers import (
    CollectionListSerializer,
    CollectionDetailSerializer,
    PhotoListSerializer,
    PhotoDetailSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)


class PhotoFilter(filters.FilterSet):
    """Filter for photos."""
    collection = filters.CharFilter(field_name='collection__slug')
    location = filters.CharFilter(field_name='location_tag', lookup_expr='iexact')
    orientation = filters.ChoiceFilter(choices=Photo.ORIENTATION_CHOICES)
    material = filters.CharFilter(method='filter_by_material')
    min_price = filters.NumberFilter(method='filter_min_price')
    max_price = filters.NumberFilter(method='filter_max_price')
    featured = filters.BooleanFilter(field_name='is_featured')

    class Meta:
        model = Photo
        fields = ['collection', 'location', 'orientation', 'featured']

    def filter_by_material(self, queryset, name, value):
        """Filter photos that have variants in the specified material."""
        return queryset.filter(
            variants__material=value,
            variants__is_available=True
        ).distinct()

    def filter_min_price(self, queryset, name, value):
        """Filter photos with variants >= min price."""
        return queryset.filter(
            variants__price__gte=value,
            variants__is_available=True
        ).distinct()

    def filter_max_price(self, queryset, name, value):
        """Filter photos with variants <= max price."""
        return queryset.filter(
            variants__price__lte=value,
            variants__is_available=True
        ).distinct()


class CollectionListView(generics.ListAPIView):
    """List all active collections."""
    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionListSerializer


class CollectionDetailView(generics.RetrieveAPIView):
    """Get a single collection with its photos."""
    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionDetailSerializer
    lookup_field = 'slug'


class PhotoListView(generics.ListAPIView):
    """List all active photos with filtering."""
    serializer_class = PhotoListSerializer
    filterset_class = PhotoFilter
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'title', 'min_price']
    ordering = ['-created_at']

    def get_queryset(self):
        return Photo.objects.filter(is_active=True).select_related('collection').annotate(
            min_price=Min('variants__price', filter=models.Q(variants__is_available=True))
        )


class PhotoDetailView(generics.RetrieveAPIView):
    """Get a single photo with all variants."""
    queryset = Photo.objects.filter(is_active=True).select_related('collection')
    serializer_class = PhotoDetailSerializer
    lookup_field = 'slug'


class FeaturedPhotosView(generics.ListAPIView):
    """List featured photos for homepage."""
    queryset = Photo.objects.filter(is_active=True, is_featured=True).select_related('collection')
    serializer_class = PhotoListSerializer
    pagination_class = None


class ProductListView(generics.ListAPIView):
    """List all active products."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product_type', 'is_featured']
    ordering_fields = ['created_at', 'title', 'price']
    ordering = ['-created_at']


class ProductDetailView(generics.RetrieveAPIView):
    """Get a single product."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
```

### backend/apps/catalog/serializers.py

```python
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
```

### backend/apps/catalog/urls.py

```python
from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('collections/', views.CollectionListView.as_view(), name='collection-list'),
    path('collections/<slug:slug>/', views.CollectionDetailView.as_view(), name='collection-detail'),
    path('photos/', views.PhotoListView.as_view(), name='photo-list'),
    path('photos/featured/', views.FeaturedPhotosView.as_view(), name='photo-featured'),
    path('photos/<slug:slug>/', views.PhotoDetailView.as_view(), name='photo-detail'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
]
```

### backend/apps/catalog/admin.py

```python
from django.contrib import admin
from django.utils.html import format_html

from .models import Collection, Photo, ProductVariant, Product


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ['title', 'slug', 'is_featured', 'is_active', 'display_order']
    readonly_fields = ['slug']
    show_change_link = True

    def display_order(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    display_order.short_description = 'Created'


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'photo_count', 'is_limited_edition', 'is_active', 'display_order']
    list_filter = ['is_active', 'is_limited_edition']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    inlines = [PhotoInline]

    def photo_count(self, obj):
        return obj.photos.filter(is_active=True).count()
    photo_count.short_description = 'Photos'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'material', 'price', 'width_inches', 'height_inches', 'is_available', 'aluminyze_sku']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'collection', 'location', 'orientation', 'is_featured', 'is_active', 'image_preview', 'variant_count']
    list_filter = ['collection', 'orientation', 'is_featured', 'is_active', 'location_tag']
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    readonly_fields = ['image_preview_large', 'created_at', 'updated_at']
    inlines = [ProductVariantInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'collection', 'description')
        }),
        ('Image', {
            'fields': ('image', 'thumbnail', 'image_preview_large')
        }),
        ('Location', {
            'fields': ('location', 'location_tag', 'orientation', 'date_taken')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.thumbnail.url)
        elif obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 400px; max-height: 300px;" />', obj.image.url)
        return '-'
    image_preview_large.short_description = 'Image Preview'

    def variant_count(self, obj):
        return obj.variants.filter(is_available=True).count()
    variant_count.short_description = 'Variants'

    actions = ['make_featured', 'remove_featured', 'activate', 'deactivate']

    @admin.action(description='Mark selected photos as featured')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Remove featured status')
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description='Activate selected photos')
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected photos')
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['photo', 'size', 'material', 'price', 'is_available']
    list_filter = ['material', 'is_available', 'size']
    search_fields = ['photo__title', 'size']
    ordering = ['photo__title', 'material', 'price']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_type', 'price', 'stock_quantity', 'is_in_stock', 'is_featured', 'is_active', 'image_preview']
    list_filter = ['product_type', 'is_featured', 'is_active']
    search_fields = ['title', 'description', 'isbn']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    readonly_fields = ['image_preview_large', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'product_type', 'description', 'long_description')
        }),
        ('Images', {
            'fields': ('image', 'image_preview_large', 'additional_images')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'compare_at_price', 'sku', 'stock_quantity', 'track_inventory', 'weight_oz')
        }),
        ('Book Details', {
            'fields': ('author', 'publisher', 'publication_year', 'pages', 'dimensions', 'isbn'),
            'classes': ('collapse',),
            'description': 'Fill these fields for book products'
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 400px; max-height: 300px;" />', obj.image.url)
        return '-'
    image_preview_large.short_description = 'Image Preview'

    def is_in_stock(self, obj):
        return obj.is_in_stock
    is_in_stock.boolean = True
    is_in_stock.short_description = 'In Stock'
```

### backend/apps/orders/models.py

```python
import uuid

from django.db import models

from apps.catalog.models import ProductVariant, Product


class Cart(models.Model):
    """Session-based shopping cart."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """An item in a shopping cart - can be a photo variant or a product."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(variant__isnull=False, product__isnull=True) |
                    models.Q(variant__isnull=True, product__isnull=False)
                ),
                name='cart_item_has_variant_or_product'
            )
        ]

    def __str__(self):
        if self.variant:
            return f"{self.quantity}x {self.variant}"
        return f"{self.quantity}x {self.product}"

    @property
    def item_type(self):
        return 'variant' if self.variant else 'product'

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.price
        return self.product.price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def title(self):
        if self.variant:
            return self.variant.photo.title
        return self.product.title

    @property
    def description(self):
        if self.variant:
            return self.variant.display_name
        return self.product.get_product_type_display()

    @property
    def image(self):
        if self.variant:
            return self.variant.photo.thumbnail or self.variant.photo.image
        return self.product.image


class Order(models.Model):
    """A completed order."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    stripe_checkout_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200)
    shipping_address = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100, blank=True)
    tracking_carrier = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """Generate a unique order number like MR-240104-001."""
        from django.utils import timezone
        date_str = timezone.now().strftime('%y%m%d')
        prefix = f'MR-{date_str}'
        last_order = Order.objects.filter(
            order_number__startswith=prefix
        ).order_by('-order_number').first()
        if last_order:
            last_num = int(last_order.order_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f'{prefix}-{new_num:03d}'


class OrderItem(models.Model):
    """An item in an order - can be a photo variant or a product."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    item_title = models.CharField(max_length=200, default='')
    item_description = models.CharField(max_length=200, default='')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    aluminyze_order_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Aluminyze order ID for fulfillment tracking'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.item_title} ({self.item_description})"

    @property
    def item_type(self):
        return 'variant' if self.variant else 'product'

    def save(self, *args, **kwargs):
        if not self.item_title:
            if self.variant:
                self.item_title = self.variant.photo.title
            elif self.product:
                self.item_title = self.product.title
        if not self.item_description:
            if self.variant:
                self.item_description = self.variant.display_name
            elif self.product:
                self.item_description = self.product.get_product_type_display()
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
```

### backend/apps/orders/views.py

```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import ProductVariant, Product
from .models import Cart, CartItem, Order
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    OrderSerializer,
)


def get_or_create_cart(request):
    """Get or create a cart for the current session."""
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


class CartView(APIView):
    """View and manage shopping cart."""

    def get(self, request):
        """Get current cart contents."""
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request):
        """Clear entire cart."""
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemView(APIView):
    """Add items to cart."""

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

        return Response(
            CartSerializer(cart, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class CartItemDetailView(APIView):
    """Update or delete a cart item."""

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

        return Response(CartSerializer(cart_item.cart).data)

    def delete(self, request, item_id):
        """Remove item from cart."""
        cart_item = self.get_cart_item(request, item_id)
        if not cart_item:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = cart_item.cart
        cart_item.delete()

        return Response(CartSerializer(cart).data)


class OrderTrackingView(APIView):
    """Look up order by order number and email for customers."""

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
```

### backend/apps/orders/serializers.py

```python
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
```

### backend/apps/orders/urls.py

```python
from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/items/', views.CartItemView.as_view(), name='cart-items'),
    path('cart/items/<int:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('orders/track/', views.OrderTrackingView.as_view(), name='order-tracking'),
]
```

### backend/apps/orders/admin.py

```python
from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Cart, CartItem, Order, OrderItem
from .emails import send_shipping_notification


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['variant', 'product', 'quantity', 'total_price']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key', 'total_items', 'subtotal', 'created_at', 'updated_at']
    readonly_fields = ['id', 'session_key', 'created_at', 'updated_at']
    search_fields = ['session_key']
    ordering = ['-updated_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['item_title', 'item_description', 'quantity', 'unit_price', 'total_price', 'aluminyze_order_id']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_email', 'status_badge', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    readonly_fields = [
        'id', 'order_number', 'stripe_checkout_id', 'stripe_payment_intent',
        'created_at', 'updated_at', 'shipping_address_display'
    ]
    ordering = ['-created_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Info', {
            'fields': ('id', 'order_number', 'status')
        }),
        ('Customer', {
            'fields': ('customer_name', 'customer_email', 'shipping_address_display')
        }),
        ('Payment', {
            'fields': ('stripe_checkout_id', 'stripe_payment_intent')
        }),
        ('Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Shipping & Tracking', {
            'fields': ('tracking_number', 'tracking_carrier'),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'processing': 'blue',
            'shipped': 'purple',
            'delivered': 'darkgreen',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def shipping_address_display(self, obj):
        addr = obj.shipping_address
        if not addr:
            return '-'
        lines = [
            addr.get('line1', ''),
            addr.get('line2', ''),
            f"{addr.get('city', '')}, {addr.get('state', '')} {addr.get('postal_code', '')}",
            addr.get('country', ''),
        ]
        return format_html('<br>'.join(line for line in lines if line.strip()))
    shipping_address_display.short_description = 'Shipping Address'

    actions = ['mark_processing', 'mark_shipped_and_notify', 'mark_delivered']

    @admin.action(description='Mark as processing')
    def mark_processing(self, request, queryset):
        updated = queryset.filter(status='paid').update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as processing.')

    @admin.action(description='Mark as shipped & send notification')
    def mark_shipped_and_notify(self, request, queryset):
        orders = queryset.filter(status='processing')
        count = 0
        for order in orders:
            order.status = 'shipped'
            order.save()
            try:
                send_shipping_notification(
                    order,
                    tracking_number=order.tracking_number or None,
                    carrier=order.tracking_carrier or None
                )
                count += 1
            except Exception:
                messages.warning(request, f'Failed to send email for order {order.order_number}')
        self.message_user(request, f'{count} order(s) marked as shipped and notified.')

    @admin.action(description='Mark as delivered')
    def mark_delivered(self, request, queryset):
        updated = queryset.filter(status='shipped').update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
```

### backend/apps/orders/emails.py

```python
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_order_confirmation(order):
    """Send order confirmation email to customer."""
    subject = f"Order Confirmed - {order.order_number}"

    context = {
        'order': order,
        'items': order.items.all(),
        'store_name': 'Matthew Raynor Photography',
        'support_email': 'hello@matthewraynor.com',
    }

    html_message = render_to_string('emails/order_confirmation.html', context)
    plain_message = render_to_string('emails/order_confirmation.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        html_message=html_message,
        fail_silently=False,
    )


def send_shipping_notification(order, tracking_number=None, carrier=None):
    """Send shipping notification email to customer."""
    subject = f"Your Order Has Shipped - {order.order_number}"

    context = {
        'order': order,
        'items': order.items.all(),
        'tracking_number': tracking_number,
        'carrier': carrier,
        'store_name': 'Matthew Raynor Photography',
        'support_email': 'hello@matthewraynor.com',
    }

    html_message = render_to_string('emails/shipping_notification.html', context)
    plain_message = render_to_string('emails/shipping_notification.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        html_message=html_message,
        fail_silently=False,
    )


def send_contact_form_notification(name, email, subject, message):
    """Send contact form submission to admin."""
    admin_subject = f"Contact Form: {subject}"

    context = {
        'name': name,
        'email': email,
        'subject': subject,
        'message': message,
    }

    html_message = render_to_string('emails/contact_form.html', context)
    plain_message = render_to_string('emails/contact_form.txt', context)

    send_mail(
        subject=admin_subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message,
        fail_silently=False,
    )

    # Auto-reply to sender
    send_mail(
        subject="Thank you for contacting Matthew Raynor Photography",
        message=f"Hi {name},\n\nThank you for reaching out. I've received your message and will get back to you within 24-48 hours.\n\nBest,\nMatt",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
```

### backend/apps/payments/views.py

```python
import stripe
from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Cart, Order, OrderItem
from apps.orders.views import get_or_create_cart
from apps.orders.emails import send_order_confirmation
from apps.core.models import GiftCard
from apps.core.emails import send_gift_card_email, send_gift_card_purchase_confirmation

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    """Create a Stripe Checkout session for the current cart."""

    def post(self, request):
        cart = get_or_create_cart(request)

        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        line_items = []
        for item in cart.items.select_related('variant__photo', 'product'):
            if item.variant:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item.variant.price * 100),
                        'product_data': {
                            'name': item.variant.photo.title,
                            'description': item.variant.display_name,
                            'images': [
                                request.build_absolute_uri(item.variant.photo.image.url)
                            ] if item.variant.photo.image else [],
                        },
                    },
                    'quantity': item.quantity,
                })
            elif item.product:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item.product.price * 100),
                        'product_data': {
                            'name': item.product.title,
                            'description': item.product.get_product_type_display(),
                            'images': [
                                request.build_absolute_uri(item.product.image.url)
                            ] if item.product.image else [],
                        },
                    },
                    'quantity': item.quantity,
                })

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/order/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/cart",
                shipping_address_collection={
                    'allowed_countries': ['US'],
                },
                billing_address_collection='required',
                metadata={
                    'cart_id': str(cart.id),
                },
            )

            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
            })

        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Handle Stripe webhook events."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})

            # Check if this is a gift card purchase
            if metadata.get('type') == 'gift_card':
                self.handle_gift_card_purchase(session)
            else:
                self.handle_checkout_completed(session)

        return HttpResponse(status=200)

    def handle_checkout_completed(self, session):
        """Create order from completed checkout session."""
        cart_id = session.get('metadata', {}).get('cart_id')
        if not cart_id:
            return

        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return

        shipping = session.get('shipping_details', {})
        address = shipping.get('address', {})

        order = Order.objects.create(
            stripe_checkout_id=session['id'],
            stripe_payment_intent=session.get('payment_intent', ''),
            customer_email=session.get('customer_details', {}).get('email', ''),
            customer_name=shipping.get('name', ''),
            shipping_address={
                'line1': address.get('line1', ''),
                'line2': address.get('line2', ''),
                'city': address.get('city', ''),
                'state': address.get('state', ''),
                'postal_code': address.get('postal_code', ''),
                'country': address.get('country', ''),
            },
            status='paid',
            subtotal=cart.subtotal,
            total=session.get('amount_total', 0) / 100,
        )

        for item in cart.items.select_related('variant__photo', 'product'):
            if item.variant:
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    item_title=item.variant.photo.title,
                    item_description=item.variant.display_name,
                    quantity=item.quantity,
                    unit_price=item.variant.price,
                    total_price=item.total_price,
                )
            elif item.product:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    item_title=item.product.title,
                    item_description=item.product.get_product_type_display(),
                    quantity=item.quantity,
                    unit_price=item.product.price,
                    total_price=item.total_price,
                )
                # Decrement stock if tracking inventory
                if item.product.track_inventory:
                    item.product.stock_quantity -= item.quantity
                    item.product.save()

        cart.items.all().delete()

        # Send confirmation email
        try:
            send_order_confirmation(order)
        except Exception:
            pass  # Don't fail the order if email fails

    def handle_gift_card_purchase(self, session):
        """Create gift card from completed checkout session."""
        metadata = session.get('metadata', {})

        amount = Decimal(metadata.get('amount', '0'))
        if amount <= 0:
            return

        gift_card = GiftCard.objects.create(
            initial_amount=amount,
            remaining_balance=amount,
            purchaser_email=metadata.get('purchaser_email', ''),
            purchaser_name=metadata.get('purchaser_name', ''),
            recipient_email=metadata.get('recipient_email', ''),
            recipient_name=metadata.get('recipient_name', ''),
            message=metadata.get('message', ''),
            stripe_payment_intent=session.get('payment_intent', ''),
        )

        # Send emails
        try:
            send_gift_card_email(gift_card)
            gift_card.mark_sent()
        except Exception:
            pass

        try:
            send_gift_card_purchase_confirmation(gift_card)
        except Exception:
            pass


class OrderLookupView(APIView):
    """Look up order by Stripe session ID."""

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(stripe_checkout_id=session_id)
            return Response({
                'order_number': order.order_number,
                'customer_email': order.customer_email,
                'total': str(order.total),
                'status': order.status,
            })
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
```

### backend/apps/payments/urls.py

```python
from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.CreateCheckoutSessionView.as_view(), name='checkout'),
    path('webhooks/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('order/', views.OrderLookupView.as_view(), name='order-lookup'),
]
```

### backend/apps/core/models.py

```python
import secrets
import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    """Newsletter subscriber."""

    SOURCE_CHOICES = [
        ('footer', 'Footer'),
        ('popup', 'Popup'),
        ('checkout', 'Checkout'),
        ('homepage', 'Homepage'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='footer')
    interests = models.JSONField(default=list, blank=True)  # Collection slugs
    is_active = models.BooleanField(default=True)
    mailerlite_id = models.CharField(max_length=100, blank=True)  # MailerLite subscriber ID
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

    def unsubscribe(self):
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()


class GiftCard(models.Model):
    """Gift card for store credit."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=16, unique=True, editable=False)
    initial_amount = models.DecimalField(max_digits=8, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=8, decimal_places=2)

    # Purchaser info
    purchaser_email = models.EmailField()
    purchaser_name = models.CharField(max_length=200, blank=True)

    # Recipient info
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True, help_text='Personal message to recipient')

    # Status
    is_active = models.BooleanField(default=True)
    is_sent = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Payment
    stripe_payment_intent = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return f"Gift Card {self.code} (${self.remaining_balance})"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        if self.remaining_balance is None:
            self.remaining_balance = self.initial_amount
        super().save(*args, **kwargs)

    def _generate_code(self):
        """Generate a unique 16-character gift card code like XXXX-XXXX-XXXX-XXXX."""
        while True:
            code = '-'.join([
                secrets.token_hex(2).upper()
                for _ in range(4)
            ])
            if not GiftCard.objects.filter(code=code).exists():
                return code

    def redeem(self, amount):
        """Redeem a portion of the gift card. Returns amount actually redeemed."""
        if not self.is_active:
            return Decimal('0')
        if self.expires_at and timezone.now() > self.expires_at:
            return Decimal('0')

        redeemable = min(amount, self.remaining_balance)
        self.remaining_balance -= redeemable
        if self.remaining_balance == 0:
            self.is_active = False
        self.save()
        return redeemable

    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.remaining_balance <= 0:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class GiftCardRedemption(models.Model):
    """Record of gift card usage on an order."""

    gift_card = models.ForeignKey(GiftCard, on_delete=models.PROTECT, related_name='redemptions')
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='gift_card_redemptions')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} from {self.gift_card.code} on {self.order.order_number}"
```

### backend/apps/core/views.py

```python
import stripe
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.emails import send_contact_form_notification
from .models import Subscriber, GiftCard
from .emails import send_gift_card_email
from .mailerlite import add_subscriber_to_mailerlite

stripe.api_key = settings.STRIPE_SECRET_KEY


class ContactFormView(APIView):
    """Handle contact form submissions."""

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()

        if not all([name, email, message]):
            return Response(
                {'error': 'Name, email, and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not subject:
            subject = 'General Inquiry'

        try:
            send_contact_form_notification(name, email, subject, message)
            return Response({'success': True, 'message': 'Message sent successfully'})
        except Exception:
            return Response(
                {'error': 'Failed to send message. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Simple health check endpoint."""

    def get(self, request):
        return Response({'status': 'ok'})


class NewsletterSubscribeView(APIView):
    """Subscribe to newsletter."""

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        name = request.data.get('name', '').strip()
        source = request.data.get('source', 'footer')
        interests = request.data.get('interests', [])

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'source': source,
                    'interests': interests,
                }
            )

            if not created:
                # Reactivate if previously unsubscribed
                if not subscriber.is_active:
                    subscriber.is_active = True
                    subscriber.unsubscribed_at = None
                    subscriber.save()

            # Sync to MailerLite
            try:
                add_subscriber_to_mailerlite(subscriber)
            except Exception:
                pass  # Don't fail if MailerLite is down

            return Response({
                'success': True,
                'message': 'Thanks for subscribing!',
                'is_new': created
            })

        except IntegrityError:
            return Response({
                'success': True,
                'message': 'You are already subscribed!',
                'is_new': False
            })


class NewsletterUnsubscribeView(APIView):
    """Unsubscribe from newsletter."""

    def post(self, request):
        email = request.data.get('email', '').strip().lower()

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscriber = Subscriber.objects.get(email=email)
            subscriber.unsubscribe()
            return Response({'success': True, 'message': 'You have been unsubscribed.'})
        except Subscriber.DoesNotExist:
            return Response({'success': True, 'message': 'You have been unsubscribed.'})


class GiftCardPurchaseView(APIView):
    """Purchase a gift card."""

    ALLOWED_AMOUNTS = [100, 250, 500, 1000, 2500]

    def post(self, request):
        amount = request.data.get('amount')
        recipient_email = request.data.get('recipient_email', '').strip().lower()
        recipient_name = request.data.get('recipient_name', '').strip()
        purchaser_email = request.data.get('purchaser_email', '').strip().lower()
        purchaser_name = request.data.get('purchaser_name', '').strip()
        message = request.data.get('message', '').strip()

        # Validate amount
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount not in self.ALLOWED_AMOUNTS:
            return Response(
                {'error': f'Amount must be one of: {self.ALLOWED_AMOUNTS}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not recipient_email or not purchaser_email:
            return Response(
                {'error': 'Recipient and purchaser email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create Stripe checkout session for gift card
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': amount * 100,
                        'product_data': {
                            'name': f'${amount} Gift Card',
                            'description': f'Gift card for Matthew Raynor Photography',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/gift-card/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/gift-card",
                metadata={
                    'type': 'gift_card',
                    'amount': str(amount),
                    'recipient_email': recipient_email,
                    'recipient_name': recipient_name,
                    'purchaser_email': purchaser_email,
                    'purchaser_name': purchaser_name,
                    'message': message[:500],  # Limit message length
                },
            )

            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
            })

        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GiftCardCheckView(APIView):
    """Check gift card balance."""

    def post(self, request):
        code = request.data.get('code', '').strip().upper()

        if not code:
            return Response(
                {'error': 'Gift card code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            gift_card = GiftCard.objects.get(code=code)

            if not gift_card.is_valid:
                return Response({
                    'valid': False,
                    'error': 'This gift card is no longer valid',
                })

            return Response({
                'valid': True,
                'balance': str(gift_card.remaining_balance),
                'expires_at': gift_card.expires_at.isoformat() if gift_card.expires_at else None,
            })

        except GiftCard.DoesNotExist:
            return Response(
                {'error': 'Gift card not found'},
                status=status.HTTP_404_NOT_FOUND
            )
```

### backend/apps/core/urls.py

```python
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),
    # Gift Cards
    path('gift-cards/purchase/', views.GiftCardPurchaseView.as_view(), name='gift-card-purchase'),
    path('gift-cards/check/', views.GiftCardCheckView.as_view(), name='gift-card-check'),
]
```

### backend/apps/core/admin.py

```python
from django.contrib import admin
from django.utils.html import format_html

from .models import Subscriber, GiftCard, GiftCardRedemption


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'source', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'source', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at', 'unsubscribed_at', 'mailerlite_id']
    ordering = ['-subscribed_at']

    actions = ['export_active_subscribers']

    def export_active_subscribers(self, request, queryset):
        """Export selected subscribers as CSV."""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'

        writer = csv.writer(response)
        writer.writerow(['Email', 'Name', 'Source', 'Subscribed At'])

        for subscriber in queryset.filter(is_active=True):
            writer.writerow([
                subscriber.email,
                subscriber.name,
                subscriber.source,
                subscriber.subscribed_at.strftime('%Y-%m-%d'),
            ])

        return response

    export_active_subscribers.short_description = "Export selected as CSV"


class GiftCardRedemptionInline(admin.TabularInline):
    model = GiftCardRedemption
    extra = 0
    readonly_fields = ['order', 'amount', 'redeemed_at']
    can_delete = False


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'initial_amount', 'remaining_balance',
        'purchaser_email', 'recipient_email', 'status_badge', 'purchased_at'
    ]
    list_filter = ['is_active', 'is_sent', 'purchased_at']
    search_fields = ['code', 'purchaser_email', 'recipient_email']
    readonly_fields = [
        'id', 'code', 'initial_amount', 'purchased_at', 'sent_at',
        'stripe_payment_intent'
    ]
    ordering = ['-purchased_at']
    inlines = [GiftCardRedemptionInline]

    fieldsets = (
        ('Gift Card Details', {
            'fields': ('id', 'code', 'initial_amount', 'remaining_balance', 'expires_at')
        }),
        ('Purchaser', {
            'fields': ('purchaser_email', 'purchaser_name')
        }),
        ('Recipient', {
            'fields': ('recipient_email', 'recipient_name', 'message')
        }),
        ('Status', {
            'fields': ('is_active', 'is_sent', 'purchased_at', 'sent_at')
        }),
        ('Stripe', {
            'fields': ('stripe_payment_intent',),
            'classes': ('collapse',)
        }),
    )

    actions = ['resend_gift_card']

    def status_badge(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: #999;">Deactivated</span>')
        if obj.remaining_balance == 0:
            return format_html('<span style="color: #666;">Used</span>')
        if obj.remaining_balance < obj.initial_amount:
            return format_html('<span style="color: #0077B6;">Partial (${:.0f})</span>', obj.remaining_balance)
        return format_html('<span style="color: #28a745;">Active</span>')

    status_badge.short_description = 'Status'

    def resend_gift_card(self, request, queryset):
        """Resend gift card emails."""
        from .emails import send_gift_card_email

        count = 0
        for gift_card in queryset:
            if gift_card.is_active and gift_card.remaining_balance > 0:
                try:
                    send_gift_card_email(gift_card)
                    count += 1
                except Exception:
                    pass

        self.message_user(request, f"Resent {count} gift card(s).")

    resend_gift_card.short_description = "Resend gift card email"
```

### backend/config/settings/base.py

```python
"""
Base Django settings for Photography Store.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'django_filters',
    'corsheaders',
    'storages',
    # Local apps
    'apps.core',
    'apps.catalog',
    'apps.orders',
    'apps.payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Session settings for cart
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days

# Stripe
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# Frontend URL for Stripe redirects
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# AWS S3 Settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_FILE_OVERWRITE = False

# Email settings
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Matt <hello@matthewraynor.com>')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'hello@matthewraynor.com')

# MailerLite (newsletter)
MAILERLITE_API_KEY = os.getenv('MAILERLITE_API_KEY', '')

# Store info (for emails)
STORE_NAME = 'Matthew Raynor Photography'
STORE_URL = os.getenv('FRONTEND_URL', 'https://store.matthewraynor.com')
```

### backend/config/settings/development.py

```python
"""
Development settings for Photography Store.
"""
import os

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'backend']

# Database - PostgreSQL via Docker or SQLite fallback
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    import re
    match = re.match(r'postgres://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<name>.+)', DATABASE_URL)
    if match:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': match.group('name'),
                'USER': match.group('user'),
                'PASSWORD': match.group('password'),
                'HOST': match.group('host'),
                'PORT': match.group('port'),
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# CORS - Allow all in development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Use local file storage in development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Email - Console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### backend/config/settings/production.py

```python
"""
Production settings for Photography Store.
"""
import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'photography_store'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# CORS - Restrict to frontend domain
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# S3 storage for production
DEFAULT_FILE_STORAGE = 'apps.core.storage.PublicMediaStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Media URL for S3
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email - SMTP (works with Resend, Postmark, etc.)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.resend.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'resend')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
```

### backend/config/urls.py

```python
"""
URL configuration for Photography Store.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.catalog.urls')),
    path('api/', include('apps.orders.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### backend/requirements.txt

```text
django>=5.0
djangorestframework>=3.14
django-filter>=24.0
django-cors-headers>=4.3
django-storages[s3]>=1.14
boto3>=1.34
stripe>=7.0
psycopg2-binary>=2.9
python-dotenv>=1.0
Pillow>=10.0
gunicorn>=21.0
```

### backend/Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production || true

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### backend/.env.example

```text
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (production)
DB_NAME=photography_store
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Stripe
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# Frontend
FRONTEND_URL=http://localhost:3000

# Email (Resend SMTP)
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=Matt <hello@matthewraynor.com>
ADMIN_EMAIL=hello@matthewraynor.com

# MailerLite (newsletter)
MAILERLITE_API_KEY=

# Production
ALLOWED_HOSTS=store.matthewraynor.com
CORS_ALLOWED_ORIGINS=https://store.matthewraynor.com
```

### frontend/src/app/layout.tsx

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Matthew Raynor Photography | Fine Art Prints of the Hamptons",
  description: "Museum-quality fine art photography prints of the Hamptons. Limited edition aluminum and archival paper prints.",
  keywords: ["Hamptons photography", "fine art prints", "beach photography", "landscape photography", "Matthew Raynor"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased bg-white text-gray-900`}>
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
```

### frontend/src/app/page.tsx

```tsx
import Link from 'next/link';
import Image from 'next/image';
import { getFeaturedPhotos, getCollections } from '@/lib/api';
import PhotoCard from '@/components/PhotoCard';

export default async function HomePage() {
  let featuredPhotos = [];
  let collections = [];

  try {
    [featuredPhotos, { results: collections }] = await Promise.all([
      getFeaturedPhotos(),
      getCollections(),
    ]);
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }

  return (
    <div>
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center bg-gray-900">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-gray-900/50" />
        <div className="relative z-10 text-center text-white px-4">
          <h1 className="text-4xl md:text-6xl font-light tracking-wide mb-4">
            Matthew Raynor Photography
          </h1>
          <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Fine art prints of the Hamptons. Museum-quality archival paper and aluminum prints.
          </p>
          <Link
            href="/collections"
            className="inline-block px-8 py-3 bg-white text-gray-900 text-sm font-medium rounded hover:bg-gray-100 transition"
          >
            Explore Collections
          </Link>
        </div>
      </section>

      {/* Featured Photos */}
      {featuredPhotos.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-light tracking-wide mb-2">Featured Works</h2>
            <p className="text-gray-600">Curated selections from the collection</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredPhotos.slice(0, 6).map((photo) => (
              <PhotoCard key={photo.id} photo={photo} />
            ))}
          </div>
          <div className="text-center mt-12">
            <Link
              href="/photos"
              className="inline-block px-8 py-3 border border-gray-900 text-gray-900 text-sm font-medium rounded hover:bg-gray-900 hover:text-white transition"
            >
              View All Prints
            </Link>
          </div>
        </section>
      )}

      {/* Collections */}
      {collections.length > 0 && (
        <section className="bg-gray-50 py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-2xl font-light tracking-wide mb-2">Collections</h2>
              <p className="text-gray-600">Explore themed series of photographs</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {collections.map((collection) => (
                <Link
                  key={collection.id}
                  href={`/collections/${collection.slug}`}
                  className="group block"
                >
                  <div className="relative aspect-[3/2] overflow-hidden bg-gray-200 rounded-sm">
                    {collection.cover_image ? (
                      <Image
                        src={collection.cover_image}
                        alt={collection.name}
                        fill
                        className="object-cover transition-transform duration-500 group-hover:scale-105"
                        sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        {collection.name}
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black/30 group-hover:bg-black/40 transition" />
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
                      <h3 className="text-xl font-medium">{collection.name}</h3>
                      <p className="text-sm text-gray-200 mt-1">{collection.photo_count} prints</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* About Teaser */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-2xl font-light tracking-wide mb-6">About the Artist</h2>
        <p className="text-gray-600 leading-relaxed mb-8">
          Matthew Raynor captures the timeless beauty of the Hamptons through fine art photography.
          Each print is produced using museum-quality materials, from archival pigment inks to
          hand-finished aluminum panels, ensuring your piece will be treasured for generations.
        </p>
        <Link
          href="/about"
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          Learn More
        </Link>
      </section>

      {/* Gift Cards CTA */}
      <section className="bg-blue-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-light tracking-wide mb-4">Give the Gift of Art</h2>
          <p className="text-blue-100 mb-8">
            Share the beauty of the Hamptons with a gift card for any occasion.
          </p>
          <Link
            href="/gift-cards"
            className="inline-block px-8 py-3 bg-white text-blue-600 text-sm font-medium rounded hover:bg-gray-100 transition"
          >
            Purchase Gift Card
          </Link>
        </div>
      </section>
    </div>
  );
}
```

### frontend/src/app/photos/page.tsx

```tsx
'use client';

import { useState, useEffect } from 'react';
import { getPhotos } from '@/lib/api';
import PhotoCard from '@/components/PhotoCard';
import type { Photo } from '@/types';

export default function PhotosPage() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    orientation: '',
    material: '',
    ordering: '-created_at',
  });

  useEffect(() => {
    const fetchPhotos = async () => {
      setLoading(true);
      try {
        const params: Record<string, string> = {};
        if (filters.orientation) params.orientation = filters.orientation;
        if (filters.material) params.material = filters.material;
        if (filters.ordering) params.ordering = filters.ordering;

        const data = await getPhotos(params);
        setPhotos(data.results || []);
      } catch (error) {
        console.error('Failed to fetch photos:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPhotos();
  }, [filters]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Shop All Prints</h1>
        <p className="text-gray-600">
          Browse our complete collection of fine art photography prints.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 justify-center mb-12">
        <select
          value={filters.orientation}
          onChange={(e) => setFilters({ ...filters, orientation: e.target.value })}
          className="px-4 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Orientations</option>
          <option value="horizontal">Horizontal</option>
          <option value="vertical">Vertical</option>
          <option value="square">Square</option>
        </select>

        <select
          value={filters.material}
          onChange={(e) => setFilters({ ...filters, material: e.target.value })}
          className="px-4 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Materials</option>
          <option value="paper">Archival Paper</option>
          <option value="aluminum">Aluminum</option>
        </select>

        <select
          value={filters.ordering}
          onChange={(e) => setFilters({ ...filters, ordering: e.target.value })}
          className="px-4 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="min_price">Price: Low to High</option>
          <option value="-min_price">Price: High to Low</option>
          <option value="title">Title A-Z</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
        </div>
      ) : photos.length === 0 ? (
        <p className="text-center text-gray-500">No photos found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {photos.map((photo) => (
            <PhotoCard key={photo.id} photo={photo} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### frontend/src/app/photos/[slug]/page.tsx

```tsx
'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { getPhoto, addToCart } from '@/lib/api';
import type { Photo, ProductVariant } from '@/types';

export default function PhotoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [photo, setPhoto] = useState<Photo | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchPhoto = async () => {
      try {
        const data = await getPhoto(slug);
        setPhoto(data);
        // Select first available variant by default
        const firstAvailable = data.variants?.find((v) => v.is_available);
        if (firstAvailable) setSelectedVariant(firstAvailable);
      } catch (error) {
        console.error('Failed to fetch photo:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPhoto();
  }, [slug]);

  const handleAddToCart = async () => {
    if (!selectedVariant) return;

    setAdding(true);
    setMessage('');
    try {
      await addToCart(selectedVariant.id);
      setMessage('Added to cart!');
      setTimeout(() => {
        router.push('/cart');
      }, 1000);
    } catch (error) {
      setMessage('Failed to add to cart. Please try again.');
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (!photo) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-gray-500 mb-4">Photo not found</p>
        <Link href="/photos" className="text-blue-600 hover:text-blue-700">
          Browse all prints
        </Link>
      </div>
    );
  }

  const paperVariants = photo.variants?.filter((v) => v.material === 'paper' && v.is_available) || [];
  const aluminumVariants = photo.variants?.filter((v) => v.material === 'aluminum' && v.is_available) || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Image */}
        <div className="relative aspect-[4/3] bg-gray-100 rounded overflow-hidden">
          {photo.image ? (
            <Image
              src={photo.image}
              alt={photo.title}
              fill
              className="object-contain"
              sizes="(max-width: 1024px) 100vw, 50vw"
              priority
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No image available
            </div>
          )}
        </div>

        {/* Details */}
        <div>
          <Link
            href={`/collections/${photo.collection.slug}`}
            className="text-sm text-blue-600 hover:text-blue-700 mb-2 inline-block"
          >
            {photo.collection.name}
          </Link>
          <h1 className="text-3xl font-light tracking-wide mb-2">{photo.title}</h1>
          <p className="text-gray-500 mb-6">{photo.location}</p>

          {photo.description && (
            <p className="text-gray-600 mb-8 leading-relaxed">{photo.description}</p>
          )}

          {/* Variant Selection */}
          <div className="space-y-6">
            {paperVariants.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-3">Archival Paper</h3>
                <div className="flex flex-wrap gap-2">
                  {paperVariants.map((variant) => (
                    <button
                      key={variant.id}
                      onClick={() => setSelectedVariant(variant)}
                      className={`px-4 py-2 border rounded text-sm transition ${
                        selectedVariant?.id === variant.id
                          ? 'border-blue-600 bg-blue-50 text-blue-600'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {variant.size} - ${variant.price}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {aluminumVariants.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-3">Aluminum</h3>
                <div className="flex flex-wrap gap-2">
                  {aluminumVariants.map((variant) => (
                    <button
                      key={variant.id}
                      onClick={() => setSelectedVariant(variant)}
                      className={`px-4 py-2 border rounded text-sm transition ${
                        selectedVariant?.id === variant.id
                          ? 'border-blue-600 bg-blue-50 text-blue-600'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {variant.size} - ${variant.price}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Selected Variant Details */}
          {selectedVariant && (
            <div className="mt-8 p-4 bg-gray-50 rounded">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">{selectedVariant.display_name}</span>
                <span className="text-xl font-medium">${selectedVariant.price}</span>
              </div>
              <p className="text-sm text-gray-500">
                {selectedVariant.width_inches}" × {selectedVariant.height_inches}"
              </p>
            </div>
          )}

          {/* Add to Cart */}
          <button
            onClick={handleAddToCart}
            disabled={!selectedVariant || adding}
            className="mt-6 w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {adding ? 'Adding...' : 'Add to Cart'}
          </button>

          {message && (
            <p className={`mt-3 text-sm text-center ${message.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>
              {message}
            </p>
          )}

          {/* Info */}
          <div className="mt-8 pt-8 border-t border-gray-200 space-y-4 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-900 mb-1">Archival Paper Prints</h4>
              <p>Museum-quality archival pigment inks on Hahnemühle Photo Rag paper. Unframed.</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-1">Aluminum Prints</h4>
              <p>HD metal prints with vibrant colors and exceptional durability. Ready to hang with float mount.</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-1">Shipping</h4>
              <p>Free shipping on orders over $500. Most orders ship within 5-7 business days.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### frontend/src/app/collections/page.tsx

```tsx
import Link from 'next/link';
import Image from 'next/image';
import { getCollections } from '@/lib/api';

export const metadata = {
  title: 'Collections | Matthew Raynor Photography',
  description: 'Explore our curated collections of fine art Hamptons photography.',
};

export default async function CollectionsPage() {
  let collections = [];

  try {
    const data = await getCollections();
    collections = data.results || [];
  } catch (error) {
    console.error('Failed to fetch collections:', error);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Collections</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Explore themed series of photographs capturing the essence of the Hamptons.
        </p>
      </div>

      {collections.length === 0 ? (
        <p className="text-center text-gray-500">No collections available yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {collections.map((collection) => (
            <Link
              key={collection.id}
              href={`/collections/${collection.slug}`}
              className="group block"
            >
              <div className="relative aspect-[16/9] overflow-hidden bg-gray-200 rounded">
                {collection.cover_image ? (
                  <Image
                    src={collection.cover_image}
                    alt={collection.name}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                    sizes="(max-width: 768px) 100vw, 50vw"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    {collection.name}
                  </div>
                )}
                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition" />
                <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/70 to-transparent">
                  <h2 className="text-xl font-medium text-white mb-1">{collection.name}</h2>
                  <p className="text-sm text-gray-200">{collection.photo_count} prints</p>
                  {collection.is_limited_edition && (
                    <span className="inline-block mt-2 px-2 py-1 bg-white/20 text-white text-xs rounded">
                      Limited Edition
                    </span>
                  )}
                </div>
              </div>
              {collection.description && (
                <p className="mt-3 text-sm text-gray-600 line-clamp-2">{collection.description}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
```

### frontend/src/app/collections/[slug]/page.tsx

```tsx
import { notFound } from 'next/navigation';
import { getCollection } from '@/lib/api';
import PhotoCard from '@/components/PhotoCard';

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  try {
    const collection = await getCollection(slug);
    return {
      title: `${collection.name} | Matthew Raynor Photography`,
      description: collection.description || `Explore the ${collection.name} collection.`,
    };
  } catch {
    return {
      title: 'Collection Not Found',
    };
  }
}

export default async function CollectionPage({ params }: Props) {
  const { slug } = await params;

  let collection;
  try {
    collection = await getCollection(slug);
  } catch {
    notFound();
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">{collection.name}</h1>
        {collection.description && (
          <p className="text-gray-600 max-w-2xl mx-auto">{collection.description}</p>
        )}
        {collection.is_limited_edition && (
          <span className="inline-block mt-4 px-3 py-1 bg-gray-900 text-white text-sm rounded">
            Limited Edition
          </span>
        )}
      </div>

      {collection.photos?.length === 0 ? (
        <p className="text-center text-gray-500">No photos in this collection yet.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {collection.photos?.map((photo) => (
            <PhotoCard key={photo.id} photo={photo} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### frontend/src/app/book/page.tsx

```tsx
'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { getProducts, addProductToCart } from '@/lib/api';
import type { Product } from '@/types';

export default function BookPage() {
  const router = useRouter();
  const [book, setBook] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState('');
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const data = await getProducts({ product_type: 'book' });
        // Get the first (and likely only) book
        if (data.results && data.results.length > 0) {
          setBook(data.results[0]);
        }
      } catch (error) {
        console.error('Failed to fetch book:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, []);

  const handleAddToCart = async () => {
    if (!book) return;

    setAdding(true);
    setMessage('');
    try {
      await addProductToCart(book.id, quantity);
      setMessage('Added to cart!');
      setTimeout(() => {
        router.push('/cart');
      }, 1000);
    } catch (error) {
      setMessage('Failed to add to cart. Please try again.');
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (!book) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-gray-500 mb-4">Book not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Book Image */}
        <div className="relative aspect-[3/4] bg-gray-100 rounded overflow-hidden">
          {book.image ? (
            <Image
              src={book.image}
              alt={book.title}
              fill
              className="object-contain"
              sizes="(max-width: 1024px) 100vw, 50vw"
              priority
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No image available
            </div>
          )}
        </div>

        {/* Book Details */}
        <div>
          <p className="text-sm text-gray-500 uppercase tracking-wider mb-2">
            {book.product_type_display}
          </p>
          <h1 className="text-3xl font-light tracking-wide mb-2">{book.title}</h1>
          {book.author && (
            <p className="text-lg text-gray-600 mb-4">by {book.author}</p>
          )}

          {book.description && (
            <p className="text-gray-600 mb-6 leading-relaxed">{book.description}</p>
          )}

          {book.long_description && (
            <div className="mb-8 prose prose-gray max-w-none">
              <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                {book.long_description}
              </p>
            </div>
          )}

          {/* Price */}
          <div className="mb-6">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-medium">${book.price}</span>
              {book.is_on_sale && book.compare_at_price && (
                <span className="text-lg text-gray-400 line-through">
                  ${book.compare_at_price}
                </span>
              )}
            </div>
            {!book.is_in_stock && (
              <p className="text-red-600 text-sm mt-1">Out of stock</p>
            )}
          </div>

          {/* Quantity Selector */}
          {book.is_in_stock && (
            <div className="mb-6">
              <label className="text-sm font-medium mb-2 block">Quantity</label>
              <div className="flex items-center border border-gray-200 rounded w-fit">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  -
                </button>
                <span className="px-4 py-2 min-w-[50px] text-center">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  +
                </button>
              </div>
            </div>
          )}

          {/* Add to Cart */}
          <button
            onClick={handleAddToCart}
            disabled={!book.is_in_stock || adding}
            className="w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {adding ? 'Adding...' : book.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
          </button>

          {message && (
            <p className={`mt-3 text-sm text-center ${message.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>
              {message}
            </p>
          )}

          {/* Book Details */}
          <div className="mt-8 pt-8 border-t border-gray-200 space-y-3 text-sm">
            <h4 className="font-medium text-gray-900">Details</h4>
            <dl className="grid grid-cols-2 gap-2 text-gray-600">
              {book.publisher && (
                <>
                  <dt className="font-medium">Publisher</dt>
                  <dd>{book.publisher}</dd>
                </>
              )}
              {book.publication_year && (
                <>
                  <dt className="font-medium">Year</dt>
                  <dd>{book.publication_year}</dd>
                </>
              )}
              {book.pages && (
                <>
                  <dt className="font-medium">Pages</dt>
                  <dd>{book.pages}</dd>
                </>
              )}
              {book.dimensions && (
                <>
                  <dt className="font-medium">Dimensions</dt>
                  <dd>{book.dimensions}</dd>
                </>
              )}
              {book.isbn && (
                <>
                  <dt className="font-medium">ISBN</dt>
                  <dd>{book.isbn}</dd>
                </>
              )}
            </dl>
          </div>

          {/* Shipping Info */}
          <div className="mt-6 pt-6 border-t border-gray-200 text-sm text-gray-600">
            <h4 className="font-medium text-gray-900 mb-2">Shipping</h4>
            <p>Free shipping on orders over $500. Most orders ship within 3-5 business days.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### frontend/src/app/book/[slug]/page.tsx

```tsx
'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useParams, useRouter } from 'next/navigation';
import { getProduct, addProductToCart } from '@/lib/api';
import type { Product } from '@/types';

export default function BookDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [book, setBook] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState('');
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const data = await getProduct(slug);
        setBook(data);
      } catch (error) {
        console.error('Failed to fetch book:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, [slug]);

  const handleAddToCart = async () => {
    if (!book) return;

    setAdding(true);
    setMessage('');
    try {
      await addProductToCart(book.id, quantity);
      setMessage('Added to cart!');
      setTimeout(() => {
        router.push('/cart');
      }, 1000);
    } catch (error) {
      setMessage('Failed to add to cart. Please try again.');
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (!book) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-gray-500 mb-4">Book not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Book Image */}
        <div className="relative aspect-[3/4] bg-gray-100 rounded overflow-hidden">
          {book.image ? (
            <Image
              src={book.image}
              alt={book.title}
              fill
              className="object-contain"
              sizes="(max-width: 1024px) 100vw, 50vw"
              priority
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No image available
            </div>
          )}
        </div>

        {/* Book Details */}
        <div>
          <p className="text-sm text-gray-500 uppercase tracking-wider mb-2">
            {book.product_type_display}
          </p>
          <h1 className="text-3xl font-light tracking-wide mb-2">{book.title}</h1>
          {book.author && (
            <p className="text-lg text-gray-600 mb-4">by {book.author}</p>
          )}

          {book.description && (
            <p className="text-gray-600 mb-6 leading-relaxed">{book.description}</p>
          )}

          {book.long_description && (
            <div className="mb-8 prose prose-gray max-w-none">
              <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                {book.long_description}
              </p>
            </div>
          )}

          {/* Price */}
          <div className="mb-6">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-medium">${book.price}</span>
              {book.is_on_sale && book.compare_at_price && (
                <span className="text-lg text-gray-400 line-through">
                  ${book.compare_at_price}
                </span>
              )}
            </div>
            {!book.is_in_stock && (
              <p className="text-red-600 text-sm mt-1">Out of stock</p>
            )}
          </div>

          {/* Quantity Selector */}
          {book.is_in_stock && (
            <div className="mb-6">
              <label className="text-sm font-medium mb-2 block">Quantity</label>
              <div className="flex items-center border border-gray-200 rounded w-fit">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  -
                </button>
                <span className="px-4 py-2 min-w-[50px] text-center">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  +
                </button>
              </div>
            </div>
          )}

          {/* Add to Cart */}
          <button
            onClick={handleAddToCart}
            disabled={!book.is_in_stock || adding}
            className="w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {adding ? 'Adding...' : book.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
          </button>

          {message && (
            <p className={`mt-3 text-sm text-center ${message.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>
              {message}
            </p>
          )}

          {/* Book Details */}
          <div className="mt-8 pt-8 border-t border-gray-200 space-y-3 text-sm">
            <h4 className="font-medium text-gray-900">Details</h4>
            <dl className="grid grid-cols-2 gap-2 text-gray-600">
              {book.publisher && (
                <>
                  <dt className="font-medium">Publisher</dt>
                  <dd>{book.publisher}</dd>
                </>
              )}
              {book.publication_year && (
                <>
                  <dt className="font-medium">Year</dt>
                  <dd>{book.publication_year}</dd>
                </>
              )}
              {book.pages && (
                <>
                  <dt className="font-medium">Pages</dt>
                  <dd>{book.pages}</dd>
                </>
              )}
              {book.dimensions && (
                <>
                  <dt className="font-medium">Dimensions</dt>
                  <dd>{book.dimensions}</dd>
                </>
              )}
              {book.isbn && (
                <>
                  <dt className="font-medium">ISBN</dt>
                  <dd>{book.isbn}</dd>
                </>
              )}
            </dl>
          </div>

          {/* Shipping Info */}
          <div className="mt-6 pt-6 border-t border-gray-200 text-sm text-gray-600">
            <h4 className="font-medium text-gray-900 mb-2">Shipping</h4>
            <p>Free shipping on orders over $500. Most orders ship within 3-5 business days.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### frontend/src/app/cart/page.tsx

```tsx
'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { getCart, updateCartItem, removeCartItem, createCheckoutSession } from '@/lib/api';
import type { Cart } from '@/types';

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<number | null>(null);
  const [checkingOut, setCheckingOut] = useState(false);

  const fetchCart = async () => {
    try {
      const data = await getCart();
      setCart(data);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleUpdateQuantity = async (itemId: number, quantity: number) => {
    if (quantity < 1) return;
    setUpdating(itemId);
    try {
      await updateCartItem(itemId, quantity);
      await fetchCart();
    } catch (error) {
      console.error('Failed to update quantity:', error);
    } finally {
      setUpdating(null);
    }
  };

  const handleRemove = async (itemId: number) => {
    setUpdating(itemId);
    try {
      await removeCartItem(itemId);
      await fetchCart();
    } catch (error) {
      console.error('Failed to remove item:', error);
    } finally {
      setUpdating(null);
    }
  };

  const handleCheckout = async () => {
    setCheckingOut(true);
    try {
      const { checkout_url } = await createCheckoutSession();
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      setCheckingOut(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 className="text-3xl font-light tracking-wide mb-4">Your Cart</h1>
        <p className="text-gray-500 mb-8">Your cart is empty.</p>
        <Link
          href="/photos"
          className="inline-block px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl font-light tracking-wide mb-8">Your Cart</h1>

      <div className="space-y-6">
        {cart.items.map((item) => {
          const itemLink = item.item_type === 'variant' && item.variant
            ? `/photos/${item.variant.photo.slug}`
            : item.product
              ? `/book/${item.product.slug}`
              : '#';

          return (
            <div
              key={item.id}
              className="flex gap-6 p-4 bg-gray-50 rounded"
            >
              {/* Image */}
              <div className="relative w-24 h-24 bg-gray-200 rounded overflow-hidden flex-shrink-0">
                {item.image ? (
                  <Image
                    src={item.image}
                    alt={item.title}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                    No image
                  </div>
                )}
              </div>

              {/* Details */}
              <div className="flex-1">
                <Link
                  href={itemLink}
                  className="font-medium hover:text-blue-600 transition"
                >
                  {item.title}
                </Link>
                <p className="text-sm text-gray-500 mt-1">{item.description}</p>

                <div className="flex items-center gap-4 mt-3">
                  <div className="flex items-center border border-gray-200 rounded">
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                      disabled={updating === item.id || item.quantity <= 1}
                      className="px-3 py-1 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                    >
                      -
                    </button>
                    <span className="px-3 py-1 min-w-[40px] text-center">{item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                      disabled={updating === item.id}
                      className="px-3 py-1 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                    >
                      +
                    </button>
                  </div>

                  <button
                    onClick={() => handleRemove(item.id)}
                    disabled={updating === item.id}
                    className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50"
                  >
                    Remove
                  </button>
                </div>
              </div>

              {/* Price */}
              <div className="text-right">
                <p className="font-medium">${item.total_price}</p>
                {item.quantity > 1 && (
                  <p className="text-sm text-gray-500">${item.unit_price} each</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <div className="flex justify-between items-center mb-6">
          <span className="text-lg">Subtotal</span>
          <span className="text-2xl font-medium">${cart.subtotal}</span>
        </div>
        <p className="text-sm text-gray-500 mb-6">
          Shipping and taxes calculated at checkout.
        </p>

        <button
          onClick={handleCheckout}
          disabled={checkingOut}
          className="w-full py-4 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50"
        >
          {checkingOut ? 'Redirecting to Checkout...' : 'Proceed to Checkout'}
        </button>

        <Link
          href="/photos"
          className="block text-center mt-4 text-sm text-gray-600 hover:text-gray-900"
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
}
```

### frontend/src/app/gift-cards/page.tsx

```tsx
'use client';

import { useState } from 'react';
import { purchaseGiftCard } from '@/lib/api';

const AMOUNTS = [100, 250, 500, 1000, 2500];

export default function GiftCardsPage() {
  const [selectedAmount, setSelectedAmount] = useState(250);
  const [recipientEmail, setRecipientEmail] = useState('');
  const [recipientName, setRecipientName] = useState('');
  const [purchaserEmail, setPurchaserEmail] = useState('');
  const [purchaserName, setPurchaserName] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { checkout_url } = await purchaseGiftCard({
        amount: selectedAmount,
        recipient_email: recipientEmail,
        recipient_name: recipientName,
        purchaser_email: purchaserEmail,
        purchaser_name: purchaserName,
        message,
      });
      window.location.href = checkout_url;
    } catch (err) {
      setError('Failed to process gift card. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Gift Cards</h1>
        <p className="text-gray-600">
          Give the gift of fine art photography. Perfect for any occasion.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Amount Selection */}
        <div>
          <label className="block text-sm font-medium mb-3">Select Amount</label>
          <div className="grid grid-cols-5 gap-2">
            {AMOUNTS.map((amount) => (
              <button
                key={amount}
                type="button"
                onClick={() => setSelectedAmount(amount)}
                className={`py-3 rounded border text-sm font-medium transition ${
                  selectedAmount === amount
                    ? 'border-blue-600 bg-blue-50 text-blue-600'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                ${amount}
              </button>
            ))}
          </div>
        </div>

        {/* Recipient Info */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Recipient Information</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Email *</label>
              <input
                type="email"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="recipient@email.com"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Name</label>
              <input
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Recipient's name"
              />
            </div>
          </div>
        </div>

        {/* Your Info */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Your Information</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Email *</label>
              <input
                type="email"
                value={purchaserEmail}
                onChange={(e) => setPurchaserEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Name</label>
              <input
                type="text"
                value={purchaserName}
                onChange={(e) => setPurchaserName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your name"
              />
            </div>
          </div>
        </div>

        {/* Personal Message */}
        <div>
          <label className="block text-sm font-medium mb-1">Personal Message (Optional)</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={3}
            maxLength={500}
            className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add a personal message to include with the gift card..."
          />
          <p className="text-xs text-gray-500 mt-1">{message.length}/500 characters</p>
        </div>

        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading || !recipientEmail || !purchaserEmail}
          className="w-full py-4 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : `Purchase $${selectedAmount} Gift Card`}
        </button>

        <p className="text-sm text-gray-500 text-center">
          The recipient will receive their gift card via email immediately after purchase.
          Gift cards are valid for one year from the date of purchase.
        </p>
      </form>
    </div>
  );
}
```

### frontend/src/app/track-order/page.tsx

```tsx
'use client';

import { useState } from 'react';
import { trackOrder } from '@/lib/api';

interface TrackingResult {
  order_number: string;
  status: string;
  tracking_number?: string;
  tracking_carrier?: string;
  tracking_url?: string;
}

export default function TrackOrderPage() {
  const [email, setEmail] = useState('');
  const [orderNumber, setOrderNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TrackingResult | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await trackOrder(email, orderNumber);
      setResult(data);
    } catch {
      setError('Order not found. Please check your email and order number.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: string) => {
    const statuses: Record<string, { label: string; color: string }> = {
      pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
      paid: { label: 'Paid', color: 'bg-blue-100 text-blue-800' },
      processing: { label: 'Processing', color: 'bg-purple-100 text-purple-800' },
      shipped: { label: 'Shipped', color: 'bg-green-100 text-green-800' },
      delivered: { label: 'Delivered', color: 'bg-green-100 text-green-800' },
      cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-800' },
    };
    return statuses[status] || { label: status, color: 'bg-gray-100 text-gray-800' };
  };

  return (
    <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Track Your Order</h1>
        <p className="text-gray-600">
          Enter your email and order number to check the status of your order.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="The email used for your order"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Order Number</label>
          <input
            type="text"
            value={orderNumber}
            onChange={(e) => setOrderNumber(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., MR-240115-001"
          />
        </div>

        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50"
        >
          {loading ? 'Looking up...' : 'Track Order'}
        </button>
      </form>

      {result && (
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-medium">Order {result.order_number}</h2>
            <span className={`px-3 py-1 rounded-full text-sm ${getStatusDisplay(result.status).color}`}>
              {getStatusDisplay(result.status).label}
            </span>
          </div>

          {result.tracking_number ? (
            <div className="space-y-2 text-sm">
              <p>
                <span className="text-gray-500">Carrier:</span>{' '}
                {result.tracking_carrier || 'Standard Shipping'}
              </p>
              <p>
                <span className="text-gray-500">Tracking Number:</span>{' '}
                {result.tracking_url ? (
                  <a
                    href={result.tracking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    {result.tracking_number}
                  </a>
                ) : (
                  result.tracking_number
                )}
              </p>
            </div>
          ) : (
            <p className="text-sm text-gray-600">
              {result.status === 'shipped' || result.status === 'delivered'
                ? 'Tracking information will be updated shortly.'
                : 'Tracking information will be available once your order ships.'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

### frontend/src/app/order/success/page.tsx

```tsx
'use client';

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { getOrderBySession } from '@/lib/api';
import type { Order } from '@/types';

function OrderSuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) {
      setError('No order session found');
      setLoading(false);
      return;
    }

    const fetchOrder = async () => {
      try {
        const data = await getOrderBySession(sessionId);
        setOrder(data);
      } catch (err) {
        setError('Could not find your order. Please check your email for confirmation.');
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <h1 className="text-3xl font-light tracking-wide mb-4">Order Status</h1>
        <p className="text-gray-600 mb-8">{error}</p>
        <Link
          href="/"
          className="inline-block px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Return Home
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h1 className="text-3xl font-light tracking-wide mb-4">Thank You!</h1>
      <p className="text-gray-600 mb-8">
        Your order has been confirmed and a receipt has been sent to {order?.customer_email}.
      </p>

      <div className="bg-gray-50 rounded-lg p-6 mb-8">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Order Number</p>
            <p className="font-medium">{order?.order_number}</p>
          </div>
          <div>
            <p className="text-gray-500">Total</p>
            <p className="font-medium">${order?.total}</p>
          </div>
        </div>
      </div>

      <p className="text-sm text-gray-500 mb-8">
        Most orders ship within 5-7 business days. You&apos;ll receive a shipping confirmation email with tracking information once your order is on its way.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          href="/photos"
          className="px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Continue Shopping
        </Link>
        <Link
          href="/track-order"
          className="px-8 py-3 border border-gray-300 text-gray-700 text-sm font-medium rounded hover:bg-gray-50 transition"
        >
          Track Order
        </Link>
      </div>
    </div>
  );
}

export default function OrderSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    }>
      <OrderSuccessContent />
    </Suspense>
  );
}
```

### frontend/src/app/about/page.tsx

```tsx
import Link from 'next/link';

export const metadata = {
  title: 'About | Matthew Raynor Photography',
  description: 'Learn about Matthew Raynor and the fine art photography of the Hamptons.',
};

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">About</h1>
      </div>

      <div className="prose prose-lg max-w-none text-gray-600">
        <p className="lead text-xl text-gray-700 mb-8">
          Matthew Raynor is a fine art photographer based in the Hamptons, capturing the
          timeless beauty of Long Island&apos;s East End through his lens.
        </p>

        <h2 className="text-xl font-medium text-gray-900 mt-12 mb-4">The Work</h2>
        <p>
          Each photograph in this collection represents a moment of quiet beauty found
          in the landscapes, seascapes, and hidden corners of the Hamptons. From the
          golden light of summer sunsets over Montauk to the moody winter skies above
          Southampton, these images capture the essence of a place cherished by many.
        </p>

        <h2 className="text-xl font-medium text-gray-900 mt-12 mb-4">The Prints</h2>
        <p>
          Every print is produced using museum-quality materials and techniques to ensure
          your artwork will be treasured for generations. We offer two premium options:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-8">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Archival Paper</h3>
            <p className="text-sm">
              Giclée prints on Hahnemühle Photo Rag, a 100% cotton, acid-free fine art paper.
              Printed with archival pigment inks rated for 100+ years of color stability.
            </p>
          </div>
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Aluminum</h3>
            <p className="text-sm">
              HD metal prints with exceptional color vibrancy and depth. Images are infused
              directly into specially coated aluminum for a stunning, ready-to-hang display.
            </p>
          </div>
        </div>

        <h2 className="text-xl font-medium text-gray-900 mt-12 mb-4">Shipping & Handling</h2>
        <p>
          All prints are carefully packaged and shipped with insurance. Paper prints
          ship in rigid tubes, while aluminum prints ship in custom protective crates.
          Most orders ship within 5-7 business days.
        </p>

        <h2 className="text-xl font-medium text-gray-900 mt-12 mb-4">Custom Orders</h2>
        <p>
          Looking for a specific size or framing option? Need a print for a commercial
          project or special occasion? I&apos;m happy to work with you on custom orders.
        </p>
      </div>

      <div className="mt-12 text-center">
        <Link
          href="/contact"
          className="inline-block px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Get in Touch
        </Link>
      </div>
    </div>
  );
}
```

### frontend/src/app/contact/page.tsx

```tsx
'use client';

import { useState } from 'react';
import { submitContactForm } from '@/lib/api';

export default function ContactPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus('idle');

    try {
      await submitContactForm({ name, email, subject, message });
      setStatus('success');
      setName('');
      setEmail('');
      setSubject('');
      setMessage('');
    } catch {
      setStatus('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Contact</h1>
        <p className="text-gray-600">
          Have a question about a print, custom sizing, or anything else? Get in touch.
        </p>
      </div>

      {status === 'success' ? (
        <div className="text-center py-12 bg-green-50 rounded-lg">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-medium mb-2">Message Sent!</h2>
          <p className="text-gray-600">Thank you for reaching out. I&apos;ll get back to you soon.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email *</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="General Inquiry"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Message *</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required
              rows={6}
              className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {status === 'error' && (
            <p className="text-red-600 text-sm">Failed to send message. Please try again.</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      )}

      <div className="mt-12 pt-12 border-t border-gray-200 text-center text-sm text-gray-600">
        <p className="mb-2">You can also reach me directly at:</p>
        <a href="mailto:hello@matthewraynor.com" className="text-blue-600 hover:text-blue-700">
          hello@matthewraynor.com
        </a>
      </div>
    </div>
  );
}
```

### frontend/src/components/Header.tsx

```tsx
'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { getCart } from '@/lib/api';

export default function Header() {
  const [cartCount, setCartCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    getCart()
      .then((cart) => setCartCount(cart.item_count))
      .catch(() => setCartCount(0));
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-100">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="text-xl font-light tracking-wide text-gray-900">
            Matthew Raynor
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/collections" className="text-sm text-gray-600 hover:text-gray-900 transition">
              Collections
            </Link>
            <Link href="/photos" className="text-sm text-gray-600 hover:text-gray-900 transition">
              Shop All
            </Link>
            <Link href="/book" className="text-sm text-gray-600 hover:text-gray-900 transition">
              Book
            </Link>
            <Link href="/about" className="text-sm text-gray-600 hover:text-gray-900 transition">
              About
            </Link>
            <Link href="/contact" className="text-sm text-gray-600 hover:text-gray-900 transition">
              Contact
            </Link>
            <Link href="/cart" className="relative text-sm text-gray-600 hover:text-gray-900 transition">
              Cart
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-4 bg-blue-600 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            <div className="flex flex-col space-y-4">
              <Link href="/collections" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Collections
              </Link>
              <Link href="/photos" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Shop All
              </Link>
              <Link href="/book" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Book
              </Link>
              <Link href="/about" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                About
              </Link>
              <Link href="/contact" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Contact
              </Link>
              <Link href="/cart" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Cart {cartCount > 0 && `(${cartCount})`}
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
```

### frontend/src/components/Footer.tsx

```tsx
'use client';

import Link from 'next/link';
import { useState } from 'react';
import { subscribeNewsletter } from '@/lib/api';

export default function Footer() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus('loading');
    try {
      const res = await subscribeNewsletter(email);
      setStatus('success');
      setMessage(res.message);
      setEmail('');
    } catch {
      setStatus('error');
      setMessage('Something went wrong. Please try again.');
    }
  };

  return (
    <footer className="bg-gray-50 border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <h3 className="text-lg font-light tracking-wide mb-4">Matthew Raynor Photography</h3>
            <p className="text-sm text-gray-600 mb-6 max-w-md">
              Fine art photography prints of the Hamptons. Museum-quality archival paper and aluminum prints for collectors and art enthusiasts.
            </p>

            {/* Newsletter */}
            <form onSubmit={handleSubscribe} className="flex gap-2 max-w-sm">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="flex-1 px-4 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={status === 'loading'}
                className="px-4 py-2 bg-gray-900 text-white text-sm rounded hover:bg-gray-800 transition disabled:opacity-50"
              >
                {status === 'loading' ? '...' : 'Subscribe'}
              </button>
            </form>
            {message && (
              <p className={`mt-2 text-sm ${status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                {message}
              </p>
            )}
          </div>

          {/* Links */}
          <div>
            <h4 className="text-sm font-medium mb-4">Shop</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/collections" className="hover:text-gray-900">Collections</Link></li>
              <li><Link href="/photos" className="hover:text-gray-900">All Prints</Link></li>
              <li><Link href="/gift-cards" className="hover:text-gray-900">Gift Cards</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-medium mb-4">Info</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/about" className="hover:text-gray-900">About</Link></li>
              <li><Link href="/contact" className="hover:text-gray-900">Contact</Link></li>
              <li><Link href="/track-order" className="hover:text-gray-900">Track Order</Link></li>
              <li><Link href="/shipping" className="hover:text-gray-900">Shipping & Returns</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-200 text-center text-sm text-gray-500">
          <p>&copy; {new Date().getFullYear()} Matthew Raynor Photography. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
```

### frontend/src/components/PhotoCard.tsx

```tsx
import Image from 'next/image';
import Link from 'next/link';
import type { Photo } from '@/types';

interface PhotoCardProps {
  photo: Photo;
}

export default function PhotoCard({ photo }: PhotoCardProps) {
  const imageUrl = photo.thumbnail || photo.image;

  return (
    <Link href={`/photos/${photo.slug}`} className="group block">
      <div className="relative aspect-[4/3] overflow-hidden bg-gray-100 rounded-sm">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt={photo.title}
            fill
            className="object-cover transition-transform duration-500 group-hover:scale-105"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No image
          </div>
        )}
      </div>
      <div className="mt-3">
        <h3 className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition">
          {photo.title}
        </h3>
        <p className="text-sm text-gray-500 mt-1">{photo.location}</p>
        {photo.min_price && (
          <p className="text-sm text-gray-700 mt-1">From ${photo.min_price}</p>
        )}
      </div>
    </Link>
  );
}
```

### frontend/src/lib/api.ts

```typescript
// Server-side uses internal Docker network, client-side uses browser-accessible URL
const getApiUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side: use Docker service name
    return process.env.INTERNAL_API_URL || 'http://backend:7974/api';
  }
  // Client-side: use browser-accessible URL
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7974/api';
};

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${getApiUrl()}${endpoint}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }

  return res.json();
}

// Collections
export async function getCollections() {
  return fetchApi<{ results: import('@/types').Collection[] }>('/collections/');
}

export async function getCollection(slug: string) {
  return fetchApi<import('@/types').Collection & { photos: import('@/types').Photo[] }>(
    `/collections/${slug}/`
  );
}

// Photos
export async function getPhotos(params?: Record<string, string>) {
  const query = params ? `?${new URLSearchParams(params)}` : '';
  return fetchApi<{ results: import('@/types').Photo[] }>(`/photos/${query}`);
}

export async function getFeaturedPhotos() {
  return fetchApi<import('@/types').Photo[]>('/photos/featured/');
}

export async function getPhoto(slug: string) {
  return fetchApi<import('@/types').Photo>(`/photos/${slug}/`);
}

// Products
export async function getProducts(params?: Record<string, string>) {
  const query = params ? `?${new URLSearchParams(params)}` : '';
  return fetchApi<{ results: import('@/types').Product[] }>(`/products/${query}`);
}

export async function getProduct(slug: string) {
  return fetchApi<import('@/types').Product>(`/products/${slug}/`);
}

// Cart
export async function getCart() {
  return fetchApi<import('@/types').Cart>('/cart/');
}

export async function addToCart(variantId: number, quantity: number = 1) {
  return fetchApi<import('@/types').CartItem>('/cart/items/', {
    method: 'POST',
    body: JSON.stringify({ variant_id: variantId, quantity }),
  });
}

export async function addProductToCart(productId: number, quantity: number = 1) {
  return fetchApi<import('@/types').CartItem>('/cart/items/', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, quantity }),
  });
}

export async function updateCartItem(itemId: number, quantity: number) {
  return fetchApi<import('@/types').CartItem>(`/cart/items/${itemId}/`, {
    method: 'PUT',
    body: JSON.stringify({ quantity }),
  });
}

export async function removeCartItem(itemId: number) {
  return fetchApi<void>(`/cart/items/${itemId}/`, {
    method: 'DELETE',
  });
}

export async function clearCart() {
  return fetchApi<void>('/cart/', {
    method: 'DELETE',
  });
}

// Checkout
export async function createCheckoutSession() {
  return fetchApi<{ checkout_url: string; session_id: string }>('/checkout/', {
    method: 'POST',
  });
}

export async function getOrderBySession(sessionId: string) {
  return fetchApi<import('@/types').Order>(`/order/?session_id=${sessionId}`);
}

// Newsletter
export async function subscribeNewsletter(email: string, name?: string) {
  return fetchApi<{ success: boolean; message: string }>('/newsletter/subscribe/', {
    method: 'POST',
    body: JSON.stringify({ email, name }),
  });
}

// Gift Cards
export async function purchaseGiftCard(data: {
  amount: number;
  recipient_email: string;
  recipient_name?: string;
  purchaser_email: string;
  purchaser_name?: string;
  message?: string;
}) {
  return fetchApi<{ checkout_url: string; session_id: string }>('/gift-cards/purchase/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function checkGiftCard(code: string) {
  return fetchApi<import('@/types').GiftCardCheck>('/gift-cards/check/', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

// Contact
export async function submitContactForm(data: {
  name: string;
  email: string;
  subject?: string;
  message: string;
}) {
  return fetchApi<{ success: boolean }>('/contact/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Order Tracking
export async function trackOrder(email: string, orderNumber: string) {
  return fetchApi<{
    order_number: string;
    status: string;
    tracking_number?: string;
    tracking_carrier?: string;
    tracking_url?: string;
  }>('/orders/track/', {
    method: 'POST',
    body: JSON.stringify({ email, order_number: orderNumber }),
  });
}
```

### frontend/src/types/index.ts

```typescript
export interface Collection {
  id: number;
  name: string;
  slug: string;
  description: string;
  cover_image: string | null;
  is_limited_edition: boolean;
  photo_count: number;
}

export interface Photo {
  id: number;
  title: string;
  slug: string;
  collection: {
    id: number;
    name: string;
    slug: string;
  };
  image: string;
  thumbnail: string | null;
  description: string;
  location: string;
  location_tag: string;
  orientation: 'horizontal' | 'vertical' | 'square';
  is_featured: boolean;
  min_price: string | null;
  variants?: ProductVariant[];
}

export interface ProductVariant {
  id: number;
  size: string;
  material: 'paper' | 'aluminum';
  price: string;
  width_inches: number;
  height_inches: number;
  is_available: boolean;
  display_name: string;
}

export interface CartItem {
  id: number;
  item_type: 'variant' | 'product';
  variant?: ProductVariant & {
    photo: {
      id: number;
      title: string;
      slug: string;
      thumbnail: string | null;
    };
  };
  product?: {
    id: number;
    title: string;
    slug: string;
    image: string;
    product_type: string;
  };
  quantity: number;
  unit_price: string;
  total_price: string;
  title: string;
  description: string;
  image: string | null;
}

export interface Cart {
  items: CartItem[];
  subtotal: string;
  item_count: number;
}

export interface Order {
  order_number: string;
  customer_email: string;
  total: string;
  status: string;
}

export interface GiftCardCheck {
  valid: boolean;
  balance?: string;
  expires_at?: string;
  error?: string;
}

export interface Product {
  id: number;
  title: string;
  slug: string;
  product_type: 'book' | 'merch';
  product_type_display: string;
  description: string;
  long_description?: string;
  image: string;
  additional_images?: string[];
  price: string;
  compare_at_price?: string;
  is_in_stock: boolean;
  is_on_sale: boolean;
  is_featured: boolean;
  author?: string;
  publisher?: string;
  publication_year?: number;
  pages?: number;
  dimensions?: string;
  isbn?: string;
  stock_quantity?: number;
}

export interface ApiResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}
```

### frontend/package.json

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "next": "16.1.1",
    "react": "19.2.3",
    "react-dom": "19.2.3"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "babel-plugin-react-compiler": "1.0.0",
    "eslint": "^9",
    "eslint-config-next": "16.1.1",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}
```

### frontend/next.config.ts

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.s3.amazonaws.com',
      },
      {
        protocol: 'https',
        hostname: 's3.amazonaws.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
};

export default nextConfig;
```

### frontend/Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

### docker-compose.yml

```yaml
# ===========================================
# PORTS: Backend 7974, Frontend 3000, DB 7975
# ===========================================

services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: photography_store
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "7975:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:7974"
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "7974:7974"
    environment:
      - DEBUG=True
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DATABASE_URL=postgres://postgres:postgres@db:5432/photography_store
      - SECRET_KEY=dev-secret-key-change-in-production
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}
      - STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET:-}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
      - AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME:-}
      - AWS_S3_REGION_NAME=${AWS_S3_REGION_NAME:-us-east-1}
      - MAILERLITE_API_KEY=${MAILERLITE_API_KEY:-}
      - FRONTEND_URL=http://localhost:3000
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:7974/api
      - INTERNAL_API_URL=http://backend:7974/api
      - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-}
    depends_on:
      - backend

volumes:
  postgres_data:
  static_volume:
  media_volume:
```
