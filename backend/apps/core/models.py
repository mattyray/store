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
        ('purchase', 'Purchase'),
        ('gift_card_purchase', 'Gift Card Purchase'),
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
    code = models.CharField(max_length=19, unique=True, editable=False)
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
    stripe_payment_intent = models.CharField(max_length=200, blank=True, unique=True)

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

    def mark_sent(self):
        """Mark gift card as sent to recipient."""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save(update_fields=['is_sent', 'sent_at'])

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
