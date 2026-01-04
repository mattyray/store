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
