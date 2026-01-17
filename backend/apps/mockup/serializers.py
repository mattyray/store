from rest_framework import serializers
from .models import WallAnalysis, SavedMockup


class WallAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for WallAnalysis model."""

    class Meta:
        model = WallAnalysis
        fields = [
            'id',
            'status',
            'original_image',
            'original_width',
            'original_height',
            'depth_map',
            'wall_mask',
            'wall_bounds',
            'confidence',
            'pixels_per_inch',
            'wall_height_feet',
            'error_message',
            'created_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'original_image',
            'original_width',
            'original_height',
            'depth_map',
            'wall_mask',
            'confidence',
            'pixels_per_inch',
            'error_message',
            'created_at',
            'completed_at',
        ]


class WallAnalysisUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating WallAnalysis (manual bounds, height adjustment)."""

    class Meta:
        model = WallAnalysis
        fields = ['wall_bounds', 'wall_height_feet']

    def update(self, instance, validated_data):
        # Update wall_bounds if provided
        if 'wall_bounds' in validated_data:
            instance.wall_bounds = validated_data['wall_bounds']
            instance.status = 'manual'

        # Update wall_height_feet if provided
        if 'wall_height_feet' in validated_data:
            instance.wall_height_feet = validated_data['wall_height_feet']

        instance.save()
        return instance


class SavedMockupSerializer(serializers.ModelSerializer):
    """Serializer for SavedMockup model."""
    share_url = serializers.CharField(read_only=True)
    wall_analysis_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = SavedMockup
        fields = [
            'id',
            'wall_analysis',
            'wall_analysis_id',
            'mockup_image',
            'config',
            'share_url',
            'created_at',
        ]
        read_only_fields = ['id', 'wall_analysis', 'share_url', 'created_at']


class SaveMockupRequestSerializer(serializers.Serializer):
    """Serializer for saving a new mockup."""
    analysis_id = serializers.UUIDField()
    mockup_image = serializers.CharField()  # Base64 encoded image
    config = serializers.JSONField(required=False, default=dict)

    def validate_mockup_image(self, value):
        # Check if it's a valid base64 data URL
        if not value.startswith('data:image/'):
            raise serializers.ValidationError('Invalid image format. Expected base64 data URL.')
        return value
