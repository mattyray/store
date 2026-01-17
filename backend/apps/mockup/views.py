import base64
import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WallAnalysis, SavedMockup
from .serializers import (
    WallAnalysisSerializer,
    WallAnalysisUpdateSerializer,
    SavedMockupSerializer,
    SaveMockupRequestSerializer,
)


class UploadWallImageView(APIView):
    """Upload a wall image for analysis."""
    parser_classes = [MultiPartParser]
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate image size (10MB limit)
        if image.size > 10 * 1024 * 1024:
            return Response(
                {'error': 'Image too large (max 10MB)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate content type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if image.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid image type. Allowed: JPEG, PNG, WebP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get session key for anonymous tracking
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key or ''

        # Create analysis record
        analysis = WallAnalysis.objects.create(
            original_image=image,
            session_key=session_key,
            status='pending'
        )

        # Queue Celery task for ML processing
        try:
            from .tasks import analyze_wall_image
            analyze_wall_image.delay(str(analysis.id))
        except Exception as e:
            # If Celery isn't available, fall back to manual mode
            analysis.status = 'manual'
            analysis.error_message = 'ML processing not available. Please select wall manually.'
            # Set default bounds (full image)
            if analysis.original_width and analysis.original_height:
                analysis.wall_bounds = {
                    'top': 0,
                    'bottom': analysis.original_height,
                    'left': 0,
                    'right': analysis.original_width,
                }
            analysis.save()

        return Response(
            WallAnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED
        )


class WallAnalysisDetailView(APIView):
    """Get or update wall analysis."""
    parser_classes = [JSONParser]
    authentication_classes = []
    permission_classes = []

    def get(self, request, analysis_id):
        """Get analysis status and results."""
        try:
            analysis = WallAnalysis.objects.get(id=analysis_id)
        except WallAnalysis.DoesNotExist:
            return Response(
                {'error': 'Analysis not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(WallAnalysisSerializer(analysis).data)

    def patch(self, request, analysis_id):
        """Update analysis (manual bounds, height adjustment)."""
        try:
            analysis = WallAnalysis.objects.get(id=analysis_id)
        except WallAnalysis.DoesNotExist:
            return Response(
                {'error': 'Analysis not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WallAnalysisUpdateSerializer(
            analysis,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(WallAnalysisSerializer(analysis).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaveMockupView(APIView):
    """Save a generated mockup image."""
    parser_classes = [JSONParser]
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SaveMockupRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        analysis_id = serializer.validated_data['analysis_id']
        mockup_image_data = serializer.validated_data['mockup_image']
        config = serializer.validated_data.get('config', {})

        # Get the analysis
        try:
            analysis = WallAnalysis.objects.get(id=analysis_id)
        except WallAnalysis.DoesNotExist:
            return Response(
                {'error': 'Analysis not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Decode base64 image
        try:
            # Remove data URL prefix (e.g., "data:image/jpeg;base64,")
            if ',' in mockup_image_data:
                header, encoded = mockup_image_data.split(',', 1)
            else:
                encoded = mockup_image_data

            # Determine format from header
            if 'png' in header.lower():
                ext = 'png'
            else:
                ext = 'jpg'

            image_data = base64.b64decode(encoded)
            image_file = ContentFile(image_data, name=f'mockup_{uuid.uuid4()}.{ext}')
        except Exception as e:
            return Response(
                {'error': f'Invalid image data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create saved mockup
        mockup = SavedMockup.objects.create(
            wall_analysis=analysis,
            mockup_image=image_file,
            config=config,
        )

        return Response(
            SavedMockupSerializer(mockup).data,
            status=status.HTTP_201_CREATED
        )


class MockupDetailView(APIView):
    """Get a saved mockup for viewing/sharing."""
    authentication_classes = []
    permission_classes = []

    def get(self, request, mockup_id):
        try:
            mockup = SavedMockup.objects.select_related('wall_analysis').get(id=mockup_id)
        except SavedMockup.DoesNotExist:
            return Response(
                {'error': 'Mockup not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(SavedMockupSerializer(mockup).data)
