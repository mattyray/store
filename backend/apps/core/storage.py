from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    """Storage backend for public media files (photos)."""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    """Storage backend for private media files."""
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
