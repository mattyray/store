from django.contrib import admin
from django.utils.html import format_html

from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['variant', 'quantity', 'total_price']

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
    readonly_fields = ['photo_title', 'variant_description', 'quantity', 'unit_price', 'total_price', 'aluminyze_order_id']

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

    actions = ['mark_processing', 'mark_shipped', 'mark_delivered']

    @admin.action(description='Mark as processing')
    def mark_processing(self, request, queryset):
        queryset.filter(status='paid').update(status='processing')

    @admin.action(description='Mark as shipped')
    def mark_shipped(self, request, queryset):
        queryset.filter(status='processing').update(status='shipped')

    @admin.action(description='Mark as delivered')
    def mark_delivered(self, request, queryset):
        queryset.filter(status='shipped').update(status='delivered')
