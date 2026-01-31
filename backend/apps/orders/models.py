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
    stripe_checkout_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True, db_index=True)
    customer_email = models.EmailField(db_index=True)
    customer_name = models.CharField(max_length=200)
    shipping_address = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
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
            from django.db import IntegrityError
            # Retry up to 5 times if concurrent orders produce a collision
            for attempt in range(5):
                self.order_number = self._generate_order_number()
                try:
                    super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    if attempt == 4:
                        raise
                    self.order_number = ''  # Reset to regenerate
                    continue
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
        if self.item_title is None or self.item_title == '':
            if self.variant:
                self.item_title = self.variant.photo.title
            elif self.product:
                self.item_title = self.product.title
        if self.item_description is None or self.item_description == '':
            if self.variant:
                self.item_description = self.variant.display_name
            elif self.product:
                self.item_description = self.product.get_product_type_display()
        if self.total_price is None:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
