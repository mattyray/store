from django.contrib import admin
from django.utils.html import format_html

from .models import Collection, Photo, ProductVariant, Product


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ['title', 'slug', 'is_featured', 'is_active', 'created_date']
    readonly_fields = ['slug', 'created_date']
    show_change_link = True

    def created_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else '-'
    created_date.short_description = 'Created'


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

    actions = ['make_featured', 'remove_featured', 'activate', 'deactivate',
                'create_paper_variants', 'create_aluminum_variants', 'create_all_variants',
                'remove_paper_variants', 'remove_aluminum_variants', 'remove_all_variants']

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

    @admin.action(description='Create paper print variants (11x14, 13x19)')
    def create_paper_variants(self, request, queryset):
        created = 0
        for photo in queryset:
            for (size, material), defaults in ProductVariant.DEFAULT_PRICING.items():
                if material == 'paper':
                    _, was_created = ProductVariant.objects.get_or_create(
                        photo=photo,
                        size=size,
                        material=material,
                        defaults={
                            'price': defaults['price'],
                            'width_inches': defaults['width'],
                            'height_inches': defaults['height'],
                        }
                    )
                    if was_created:
                        created += 1
        self.message_user(request, f'Created {created} paper variants.')

    @admin.action(description='Create aluminum print variants (16x24 to 40x60)')
    def create_aluminum_variants(self, request, queryset):
        created = 0
        for photo in queryset:
            for (size, material), defaults in ProductVariant.DEFAULT_PRICING.items():
                if material == 'aluminum':
                    _, was_created = ProductVariant.objects.get_or_create(
                        photo=photo,
                        size=size,
                        material=material,
                        defaults={
                            'price': defaults['price'],
                            'width_inches': defaults['width'],
                            'height_inches': defaults['height'],
                        }
                    )
                    if was_created:
                        created += 1
        self.message_user(request, f'Created {created} aluminum variants.')

    @admin.action(description='Create ALL standard variants (paper + aluminum)')
    def create_all_variants(self, request, queryset):
        created = 0
        for photo in queryset:
            for (size, material), defaults in ProductVariant.DEFAULT_PRICING.items():
                _, was_created = ProductVariant.objects.get_or_create(
                    photo=photo,
                    size=size,
                    material=material,
                    defaults={
                        'price': defaults['price'],
                        'width_inches': defaults['width'],
                        'height_inches': defaults['height'],
                    }
                )
                if was_created:
                    created += 1
        self.message_user(request, f'Created {created} variants for {queryset.count()} photos.')

    @admin.action(description='Remove ALL paper print variants')
    def remove_paper_variants(self, request, queryset):
        deleted = ProductVariant.objects.filter(photo__in=queryset, material='paper').delete()[0]
        self.message_user(request, f'Deleted {deleted} paper variants.')

    @admin.action(description='Remove ALL aluminum print variants')
    def remove_aluminum_variants(self, request, queryset):
        deleted = ProductVariant.objects.filter(photo__in=queryset, material='aluminum').delete()[0]
        self.message_user(request, f'Deleted {deleted} aluminum variants.')

    @admin.action(description='Remove ALL variants (paper + aluminum)')
    def remove_all_variants(self, request, queryset):
        deleted = ProductVariant.objects.filter(photo__in=queryset).delete()[0]
        self.message_user(request, f'Deleted {deleted} variants from {queryset.count()} photos.')


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
