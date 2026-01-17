from django.contrib import admin
from django.utils.html import format_html
from .models import WallAnalysis, SavedMockup


@admin.register(WallAnalysis)
class WallAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'status_badge', 'confidence_display', 'wall_height_feet', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'created_at', 'completed_at', 'original_width', 'original_height']
    search_fields = ['id', 'session_key']
    ordering = ['-created_at']

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'processing': '#3b82f6',
            'completed': '#10b981',
            'manual': '#8b5cf6',
            'failed': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'

    def confidence_display(self, obj):
        if obj.confidence is None:
            return '-'
        pct = obj.confidence * 100
        color = '#10b981' if pct >= 50 else '#f59e0b' if pct >= 30 else '#ef4444'
        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color, pct
        )
    confidence_display.short_description = 'Confidence'


@admin.register(SavedMockup)
class SavedMockupAdmin(admin.ModelAdmin):
    list_display = ['id', 'wall_analysis', 'created_at', 'view_mockup']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at']
    search_fields = ['id']
    ordering = ['-created_at']

    def view_mockup(self, obj):
        if obj.mockup_image:
            return format_html(
                '<a href="{}" target="_blank">View</a>',
                obj.mockup_image.url
            )
        return '-'
    view_mockup.short_description = 'Mockup'
