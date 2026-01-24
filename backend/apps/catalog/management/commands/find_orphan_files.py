"""
Management command to find and optionally delete orphaned S3 files.

Compares files in S3 against database records to find files that no longer
have a corresponding model instance.

Usage:
    python manage.py find_orphan_files              # List orphans (dry run)
    python manage.py find_orphan_files --delete     # Delete orphans
"""
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.catalog.models import Collection, Photo, Product


class Command(BaseCommand):
    help = 'Find and optionally delete orphaned files in S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete orphaned files (default is dry run)',
        )

    def handle(self, *args, **options):
        delete = options['delete']

        if delete:
            self.stdout.write(self.style.WARNING('DELETE MODE - Files will be removed!'))
        else:
            self.stdout.write(self.style.NOTICE('DRY RUN - No files will be deleted'))

        self.stdout.write('')

        # Initialize S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        total_orphans = 0
        total_size = 0

        # Check collections
        orphans, size = self.check_prefix(
            s3, bucket, 'media/collections/',
            self.get_collection_files(),
            delete
        )
        total_orphans += orphans
        total_size += size

        # Check photos
        orphans, size = self.check_prefix(
            s3, bucket, 'media/photos/',
            self.get_photo_files(),
            delete,
            exclude_prefix='media/photos/thumbnails/'
        )
        total_orphans += orphans
        total_size += size

        # Check thumbnails
        orphans, size = self.check_prefix(
            s3, bucket, 'media/photos/thumbnails/',
            self.get_thumbnail_files(),
            delete
        )
        total_orphans += orphans
        total_size += size

        # Check products
        orphans, size = self.check_prefix(
            s3, bucket, 'media/products/',
            self.get_product_files(),
            delete
        )
        total_orphans += orphans
        total_size += size

        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 50)
        size_mb = total_size / (1024 * 1024)
        if delete:
            self.stdout.write(self.style.SUCCESS(
                f'Deleted {total_orphans} orphaned files ({size_mb:.2f} MB)'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Found {total_orphans} orphaned files ({size_mb:.2f} MB)'
            ))
            if total_orphans > 0:
                self.stdout.write(self.style.NOTICE(
                    'Run with --delete to remove them'
                ))

    def get_collection_files(self):
        """Get set of collection image paths from database."""
        files = set()
        for c in Collection.objects.all():
            if c.cover_image:
                files.add(f'media/{c.cover_image.name}')
        return files

    def get_photo_files(self):
        """Get set of photo image paths from database."""
        files = set()
        for p in Photo.objects.all():
            if p.image:
                files.add(f'media/{p.image.name}')
        return files

    def get_thumbnail_files(self):
        """Get set of thumbnail paths from database."""
        files = set()
        for p in Photo.objects.all():
            if p.thumbnail:
                files.add(f'media/{p.thumbnail.name}')
        return files

    def get_product_files(self):
        """Get set of product image paths from database."""
        files = set()
        for p in Product.objects.all():
            if p.image:
                files.add(f'media/{p.image.name}')
        return files

    def check_prefix(self, s3, bucket, prefix, db_files, delete, exclude_prefix=None):
        """Check S3 prefix for orphaned files."""
        self.stdout.write(f'\nChecking {prefix}...')

        # List all files in S3 with this prefix
        s3_files = {}
        paginator = s3.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                # Skip if this key starts with exclude_prefix
                if exclude_prefix and key.startswith(exclude_prefix):
                    continue
                s3_files[key] = obj['Size']

        # Find orphans
        orphan_count = 0
        orphan_size = 0

        for s3_key, size in s3_files.items():
            if s3_key not in db_files:
                orphan_count += 1
                orphan_size += size
                size_kb = size / 1024

                if delete:
                    s3.delete_object(Bucket=bucket, Key=s3_key)
                    self.stdout.write(self.style.ERROR(
                        f'  DELETED: {s3_key} ({size_kb:.1f} KB)'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  ORPHAN: {s3_key} ({size_kb:.1f} KB)'
                    ))

        if orphan_count == 0:
            self.stdout.write(self.style.SUCCESS(f'  No orphans found'))
        else:
            self.stdout.write(f'  Found {orphan_count} orphans in {prefix}')

        return orphan_count, orphan_size
