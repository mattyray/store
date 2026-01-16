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
        orders = queryset.filter(status__in=['paid', 'processing'])
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
