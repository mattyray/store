from django.contrib import admin
from django.utils.html import format_html

from .models import Collection, Photo, ProductVariant


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
