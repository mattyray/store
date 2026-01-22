"""
Management command to generate vector embeddings for photos.

Uses OpenAI's text-embedding-ada-002 model to create embeddings from
the AI-generated descriptions and metadata.

Usage:
    python manage.py generate_photo_embeddings
    python manage.py generate_photo_embeddings --photo-id=5
    python manage.py generate_photo_embeddings --overwrite
"""
from django.core.management.base import BaseCommand
from django.conf import settings

from openai import OpenAI

from apps.catalog.models import Photo


class Command(BaseCommand):
    help = 'Generate vector embeddings for photos using OpenAI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--photo-id',
            type=int,
            help='Process only a specific photo by ID',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing embeddings',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be done without making changes',
        )

    def handle(self, *args, **options):
        if not settings.OPENAI_API_KEY:
            self.stderr.write(self.style.ERROR(
                'OPENAI_API_KEY not set. Please add it to your environment.'
            ))
            return

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Get photos to process
        photos = Photo.objects.filter(is_active=True)

        if options['photo_id']:
            photos = photos.filter(id=options['photo_id'])

        # Only process photos with AI descriptions
        photos = photos.exclude(ai_description='')

        if not options['overwrite']:
            # Only process photos without embeddings
            photos = photos.filter(embedding__isnull=True)

        total = photos.count()
        if total == 0:
            self.stdout.write(self.style.WARNING(
                'No photos to process. Make sure photos have AI descriptions first.\n'
                'Run: python manage.py generate_photo_descriptions'
            ))
            return

        self.stdout.write(f'Processing {total} photos...\n')

        success_count = 0
        error_count = 0

        for i, photo in enumerate(photos, 1):
            self.stdout.write(f'[{i}/{total}] Processing: {photo.title}')

            try:
                # Build text for embedding
                text = self._build_embedding_text(photo)

                if options['dry_run']:
                    self.stdout.write(self.style.SUCCESS(f'  [DRY RUN] Would embed: {text[:100]}...'))
                    continue

                # Generate embedding
                embedding = self._generate_embedding(client, text)

                if embedding:
                    photo.embedding = embedding
                    photo.save(update_fields=['embedding'])

                    self.stdout.write(self.style.SUCCESS(
                        f'  Generated embedding ({len(embedding)} dimensions)'
                    ))
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error: {str(e)}'))
                error_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Completed: {success_count} successful, {error_count} errors'
        ))

    def _build_embedding_text(self, photo: Photo) -> str:
        """Build a combined text string for embedding from photo metadata."""
        parts = []

        # Title
        parts.append(f"Title: {photo.title}")

        # AI description
        if photo.ai_description:
            parts.append(f"Description: {photo.ai_description}")

        # Location
        if photo.location:
            parts.append(f"Location: {photo.location}")

        # Colors
        if photo.ai_colors:
            colors = ', '.join(photo.ai_colors)
            parts.append(f"Colors: {colors}")

        # Mood
        if photo.ai_mood:
            moods = ', '.join(photo.ai_mood)
            parts.append(f"Mood: {moods}")

        # Subjects
        if photo.ai_subjects:
            subjects = ', '.join(photo.ai_subjects)
            parts.append(f"Subjects: {subjects}")

        # Room suggestions
        if photo.ai_room_suggestions:
            rooms = ', '.join(photo.ai_room_suggestions)
            parts.append(f"Suggested rooms: {rooms}")

        # Collection
        if photo.collection:
            parts.append(f"Collection: {photo.collection.name}")

        return '\n'.join(parts)

    def _generate_embedding(self, client: OpenAI, text: str) -> list | None:
        """Generate embedding vector using OpenAI API."""
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text,
            )

            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            self.stderr.write(f'    OpenAI API error: {e}')
            return None
