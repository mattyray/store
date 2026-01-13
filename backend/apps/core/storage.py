from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    """Storage backend for public media files (photos)."""
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    location = 'media'
    default_acl = None
    file_overwrite = False
    querystring_auth = False


class PrivateMediaStorage(S3Boto3Storage):
    """Storage backend for private media files."""
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
