import uuid
from django.db import models
from PIL import Image


class WallAnalysis(models.Model):
    """Stores wall analysis results for a user-uploaded image."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('manual', 'Manual Selection'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Original image
    original_image = models.ImageField(upload_to='mockups/walls/')
    original_width = models.PositiveIntegerField(null=True, blank=True)
    original_height = models.PositiveIntegerField(null=True, blank=True)

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    error_message = models.TextField(blank=True)

    # ML Results (populated after processing)
    depth_map = models.ImageField(upload_to='mockups/depth/', blank=True, null=True)
    wall_mask = models.ImageField(upload_to='mockups/masks/', blank=True, null=True)
    wall_bounds = models.JSONField(null=True, blank=True)  # {top, bottom, left, right}
    confidence = models.FloatField(null=True, blank=True)

    # Scale information
    pixels_per_inch = models.FloatField(null=True, blank=True)
    wall_height_feet = models.FloatField(default=8.0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Session tracking (for anonymous users)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wall Analysis'
        verbose_name_plural = 'Wall Analyses'

    def __str__(self):
        return f"WallAnalysis {self.id} ({self.status})"

    def save(self, *args, **kwargs):
        # Auto-populate image dimensions
        if self.original_image and not self.original_width:
            try:
                img = Image.open(self.original_image)
                self.original_width = img.width
                self.original_height = img.height
            except Exception:
                pass

        # Calculate pixels_per_inch based on wall bounds and height
        if self.wall_bounds and self.wall_height_feet:
            wall_height_px = self.wall_bounds.get('bottom', 0) - self.wall_bounds.get('top', 0)
            if wall_height_px > 0:
                wall_height_inches = self.wall_height_feet * 12
                self.pixels_per_inch = wall_height_px / wall_height_inches

        super().save(*args, **kwargs)


class SavedMockup(models.Model):
    """Stores a user-generated mockup image for sharing."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    wall_analysis = models.ForeignKey(
        WallAnalysis,
        on_delete=models.CASCADE,
        related_name='saved_mockups'
    )

    # Generated mockup image
    mockup_image = models.ImageField(upload_to='mockups/saved/')

    # Configuration that created this mockup
    config = models.JSONField(default=dict)
    # Expected structure:
    # {
    #     "prints": [
    #         {
    #             "photo_id": 123,
    #             "variant_id": 456,
    #             "position": {"x": 100, "y": 200},
    #             "scale": 1.0
    #         }
    #     ],
    #     "wall_height_feet": 8.0
    # }

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Saved Mockup'
        verbose_name_plural = 'Saved Mockups'

    def __str__(self):
        return f"SavedMockup {self.id}"

    @property
    def share_url(self):
        """Returns the shareable URL for this mockup."""
        from django.conf import settings
        return f"{settings.STORE_URL}/mockup/{self.id}"
