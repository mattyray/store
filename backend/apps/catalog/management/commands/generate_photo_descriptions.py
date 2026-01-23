"""
Management command to generate AI descriptions for photos using Claude Vision.

Usage:
    python manage.py generate_photo_descriptions
    python manage.py generate_photo_descriptions --photo-id=5
    python manage.py generate_photo_descriptions --overwrite
"""
import base64
import json
import requests
from io import BytesIO

from django.core.management.base import BaseCommand
from django.conf import settings

import anthropic
import boto3
from botocore.exceptions import ClientError

from apps.catalog.models import Photo


class Command(BaseCommand):
    help = 'Generate AI descriptions for photos using Claude Vision'

    def add_arguments(self, parser):
        parser.add_argument(
            '--photo-id',
            type=int,
            help='Process only a specific photo by ID',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing AI descriptions',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be done without making changes',
        )

    def handle(self, *args, **options):
        if not settings.ANTHROPIC_API_KEY:
            self.stderr.write(self.style.ERROR(
                'ANTHROPIC_API_KEY not set. Please add it to your environment.'
            ))
            return

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Get photos to process
        photos = Photo.objects.filter(is_active=True)

        if options['photo_id']:
            photos = photos.filter(id=options['photo_id'])

        if not options['overwrite']:
            # Only process photos without AI descriptions
            photos = photos.filter(ai_description='')

        total = photos.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No photos to process.'))
            return

        self.stdout.write(f'Processing {total} photos...\n')

        success_count = 0
        error_count = 0

        for i, photo in enumerate(photos, 1):
            self.stdout.write(f'[{i}/{total}] Processing: {photo.title}')

            try:
                # Get image data
                image_data = self._get_image_data(photo)
                if not image_data:
                    self.stderr.write(self.style.WARNING(f'  Could not load image for {photo.title}'))
                    error_count += 1
                    continue

                if options['dry_run']:
                    self.stdout.write(self.style.SUCCESS(f'  [DRY RUN] Would process {photo.title}'))
                    continue

                # Call Claude Vision
                result = self._analyze_image(client, image_data, photo)

                if result:
                    # Update photo
                    photo.ai_description = result.get('description', '')
                    photo.ai_colors = result.get('colors', [])
                    photo.ai_mood = result.get('mood', [])
                    photo.ai_subjects = result.get('subjects', [])
                    photo.ai_room_suggestions = result.get('room_suggestions', [])
                    photo.save()

                    self.stdout.write(self.style.SUCCESS(f'  Updated: {photo.title}'))
                    self.stdout.write(f'    Colors: {photo.ai_colors}')
                    self.stdout.write(f'    Mood: {photo.ai_mood}')
                    self.stdout.write(f'    Subjects: {photo.ai_subjects}')
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error: {str(e)}'))
                error_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Completed: {success_count} successful, {error_count} errors'))

    def _get_image_data(self, photo) -> dict | None:
        """Load image from S3 and return base64 encoded data with media type."""
        try:
            if not photo.image or not photo.image.name:
                return None

            # Use boto3 to read directly from S3 with AWS credentials
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
            )

            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            # Files are stored under media/ prefix in S3
            object_key = f'media/{photo.image.name}'

            self.stdout.write(f'    Fetching from S3: {bucket_name}/{object_key}')

            # Get object from S3
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            image_bytes = response['Body'].read()

            # Determine media type from content type or file extension
            content_type = response.get('ContentType', '')
            if not content_type:
                # Fallback to extension
                ext = object_key.lower().split('.')[-1]
                content_type = {
                    'png': 'image/png',
                    'webp': 'image/webp',
                    'gif': 'image/gif',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                }.get(ext, 'image/jpeg')

            if 'png' in content_type:
                media_type = 'image/png'
            elif 'webp' in content_type:
                media_type = 'image/webp'
            elif 'gif' in content_type:
                media_type = 'image/gif'
            else:
                media_type = 'image/jpeg'

            # Base64 encode
            image_base64 = base64.standard_b64encode(image_bytes).decode('utf-8')

            return {
                'type': 'base64',
                'media_type': media_type,
                'data': image_base64,
            }

        except ClientError as e:
            self.stderr.write(f'    S3 error: {e}')
            return None
        except Exception as e:
            self.stderr.write(f'    Error loading image: {e}')
            return None

    def _analyze_image(self, client: anthropic.Anthropic, image_data: dict, photo: Photo) -> dict | None:
        """Use Claude Vision to analyze the image and extract metadata."""

        prompt = """Analyze this fine art photograph and provide the following information in JSON format:

1. "description": A rich, evocative description of the photograph (2-3 sentences). Focus on what makes it visually striking, the mood it creates, and what a buyer might find appealing. Write from a fine art perspective.

2. "colors": An array of 3-5 dominant colors in the image. Use descriptive color names like "deep ocean blue", "golden sunset", "misty gray", "warm amber", "seafoam green".

3. "mood": An array of 3-5 mood/feeling keywords that describe the emotional tone. Examples: "serene", "dramatic", "peaceful", "energetic", "contemplative", "majestic", "intimate", "nostalgic".

4. "subjects": An array of 3-7 subjects/elements visible in the image. Examples: "lighthouse", "ocean waves", "beach", "sunset", "aerial view", "boats", "harbor", "dunes", "coastline".

5. "room_suggestions": An array of 2-4 room types where this print would look great. Examples: "living room", "bedroom", "office", "beach house", "coastal home", "modern apartment", "dining room".

Respond ONLY with valid JSON, no other text. Example format:
{
  "description": "A breathtaking aerial view of...",
  "colors": ["deep blue", "sandy beige", "white foam"],
  "mood": ["serene", "expansive", "calming"],
  "subjects": ["beach", "ocean", "aerial view", "coastline"],
  "room_suggestions": ["living room", "beach house", "office"]
}"""

        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": image_data['media_type'],
                                    "data": image_data['data'],
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            }
                        ],
                    }
                ],
            )

            # Parse JSON response
            response_text = message.content[0].text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)
            return result

        except json.JSONDecodeError as e:
            self.stderr.write(f'    JSON parse error: {e}')
            self.stderr.write(f'    Response: {response_text[:200]}...')
            return None
        except Exception as e:
            self.stderr.write(f'    API error: {e}')
            return None
