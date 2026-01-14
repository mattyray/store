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
    image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
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
        # Auto-populate image dimensions
        if self.image:
            try:
                self.image_width = self.image.width
                self.image_height = self.image.height
            except Exception:
                pass  # Image not accessible yet
        super().save(*args, **kwargs)

    @property
    def aspect_ratio(self):
        """Returns the actual aspect ratio of the image."""
        if self.image_width and self.image_height:
            return self.image_width / self.image_height
        # Fallback based on orientation
        if self.orientation == 'V':
            return 2 / 3
        elif self.orientation == 'S':
            return 1
        return 3 / 2  # Default horizontal

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

    # Default pricing by size and material (width x height format)
    DEFAULT_PRICING = {
        # Paper prints (matted)
        ('14x11', 'paper'): {'price': 175, 'width': 14, 'height': 11},
        ('19x13', 'paper'): {'price': 250, 'width': 19, 'height': 13},
        # Aluminum prints
        ('24x16', 'aluminum'): {'price': 675, 'width': 24, 'height': 16},
        ('30x20', 'aluminum'): {'price': 995, 'width': 30, 'height': 20},
        ('36x24', 'aluminum'): {'price': 1350, 'width': 36, 'height': 24},
        ('40x30', 'aluminum'): {'price': 1850, 'width': 40, 'height': 30},
        ('45x30', 'aluminum'): {'price': 2150, 'width': 45, 'height': 30},
        ('60x40', 'aluminum'): {'price': 3400, 'width': 60, 'height': 40},
    }

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
