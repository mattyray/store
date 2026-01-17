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
        'id', 'code', 'purchased_at', 'sent_at',
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
            return format_html('<span style="color: {};">Deactivated</span>', '#999')
        if obj.remaining_balance == 0:
            return format_html('<span style="color: {};">Used</span>', '#666')
        if obj.remaining_balance < obj.initial_amount:
            return format_html('<span style="color: #0077B6;">Partial (${})</span>', int(obj.remaining_balance))
        return format_html('<span style="color: {};">Active</span>', '#28a745')

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
