from celery import shared_task
from django.utils import timezone


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

    try:
        analysis = WallAnalysis.objects.get(id=analysis_id)
    except WallAnalysis.DoesNotExist:
        return {'error': 'Analysis not found'}

    # Update status to processing
    analysis.status = 'processing'
    analysis.save(update_fields=['status'])

    try:
        # Import ML modules
        from .ml.depth import run_depth_estimation
        from .ml.wall import detect_wall_plane

        # Get image path
        image_path = analysis.original_image.path

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

        return {
            'status': analysis.status,
            'confidence': analysis.confidence,
        }

    except Exception as e:
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
