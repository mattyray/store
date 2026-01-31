import logging
import os
import tempfile
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_wall_analyses(hours: int = 24):
    """
    Delete WallAnalysis records older than specified hours.

    Deletes SavedMockup records individually first to ensure their S3 files
    are cleaned up (cascade SQL DELETE skips Django's file deletion).

    Args:
        hours: Delete records older than this many hours (default 24)

    Returns:
        Number of records deleted
    """
    from .models import WallAnalysis, SavedMockup

    cutoff = timezone.now() - timedelta(hours=hours)
    old_analyses = WallAnalysis.objects.filter(created_at__lt=cutoff)

    count = old_analyses.count()
    if count > 0:
        # Delete SavedMockups individually first so their S3 files are cleaned up
        # (cascade SQL DELETE doesn't trigger Django storage file deletion)
        mockups = SavedMockup.objects.filter(wall_analysis__in=old_analyses)
        for mockup in mockups:
            try:
                mockup.mockup_image.delete(save=False)
                mockup.delete()
            except Exception as e:
                logger.error(f'Failed to delete SavedMockup {mockup.id}: {e}')

        # Delete WallAnalysis records one by one to clean up their S3 files
        for analysis in old_analyses:
            try:
                analysis.delete()
            except Exception as e:
                logger.error(f'Failed to delete WallAnalysis {analysis.id}: {e}')

        logger.info(f'Cleaned up {count} old WallAnalysis records')

    return count


@shared_task(bind=True, soft_time_limit=30, time_limit=45)
def analyze_wall_image(self, analysis_id: str):
    """
    Celery task to analyze a wall image using ML.

    Steps:
    1. Load the image
    2. Run MiDaS depth estimation
    3. Detect wall plane using RANSAC
    4. Save results to database
    """
    from .models import WallAnalysis

    logger.info(f'Starting wall analysis for {analysis_id}')

    try:
        analysis = WallAnalysis.objects.get(id=analysis_id)
    except WallAnalysis.DoesNotExist:
        logger.error(f'Analysis {analysis_id} not found')
        return {'error': 'Analysis not found'}

    # Update status to processing
    analysis.status = 'processing'
    analysis.save(update_fields=['status'])

    # Track temp file for cleanup
    temp_image_path = None

    try:
        # Import ML modules
        from .ml.depth import run_depth_estimation
        from .ml.wall import detect_wall_plane

        # Download image from S3 to temp file (required for S3 storage)
        # .path doesn't work with S3, so we use .open() and write to temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            with analysis.original_image.open('rb') as img_file:
                tmp.write(img_file.read())
            temp_image_path = tmp.name

        logger.info(f'Image downloaded to temp file')
        image_path = temp_image_path

        # Run depth estimation
        depth_map = run_depth_estimation(image_path)

        if depth_map is None:
            raise Exception('Depth estimation failed')

        # Detect wall plane
        wall_data = detect_wall_plane(
            depth_map,
            image_width=analysis.original_width,
            image_height=analysis.original_height
        )

        if wall_data['confidence'] >= 0.3:
            # Successful detection
            analysis.status = 'completed'
            analysis.wall_bounds = wall_data['bounds']
            analysis.confidence = wall_data['confidence']

            # Save depth map image if available
            if 'depth_image_path' in wall_data:
                from django.core.files import File
                with open(wall_data['depth_image_path'], 'rb') as f:
                    analysis.depth_map.save(
                        f'depth_{analysis_id}.png',
                        File(f),
                        save=False
                    )
        else:
            # Low confidence - fall back to manual
            analysis.status = 'manual'
            analysis.confidence = wall_data['confidence']
            analysis.error_message = 'Could not detect wall with high confidence. Please select manually.'
            # Set default bounds (full image)
            analysis.wall_bounds = {
                'top': 0,
                'bottom': analysis.original_height,
                'left': 0,
                'right': analysis.original_width,
            }

        analysis.completed_at = timezone.now()
        analysis.save()

        logger.info(f'Wall analysis completed: status={analysis.status}, confidence={analysis.confidence}')

        return {
            'status': analysis.status,
            'confidence': analysis.confidence,
        }

    except Exception as e:
        logger.error(f'ML processing failed for {analysis_id}: {str(e)}')
        # ML processing failed
        analysis.status = 'manual'
        analysis.error_message = f'ML processing failed: {str(e)}. Please select wall manually.'
        # Set default bounds (full image)
        if analysis.original_width and analysis.original_height:
            analysis.wall_bounds = {
                'top': 0,
                'bottom': analysis.original_height,
                'left': 0,
                'right': analysis.original_width,
            }
        analysis.completed_at = timezone.now()
        analysis.save()

        return {
            'status': 'manual',
            'error': str(e),
        }

    finally:
        # Clean up temp file
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.unlink(temp_image_path)
            except Exception:
                pass
