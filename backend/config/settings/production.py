"""
Production settings for Photography Store.
"""
import os
import re

from .base import *

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Allow Railway's health check and configured hosts
# Set ALLOWED_HOSTS env var to: your-app.up.railway.app,store-api.matthewraynor.com
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]
# Add Railway's internal hostname pattern for health checks
ALLOWED_HOSTS.append('.railway.internal')

# Database - PostgreSQL for production (supports DATABASE_URL from Railway)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Parse DATABASE_URL (postgres://user:pass@host:port/dbname)
    match = re.match(
        r'(?:postgres(?:ql)?://)?(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<name>.+)',
        DATABASE_URL
    )
    if match:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': match.group('name'),
                'USER': match.group('user'),
                'PASSWORD': match.group('password'),
                'HOST': match.group('host'),
                'PORT': match.group('port'),
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'photography_store'),
            'USER': os.getenv('DB_USER', ''),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# CORS - Restrict to frontend domain
cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins.split(',') if o.strip()]
CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins (required for Django 4+ cross-origin POST)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in cors_origins.split(',') if o.strip()]

# WhiteNoise - serve static files in production
WHITENOISE_USE_FINDERS = True

# S3 storage for media files
STORAGES = {
    "default": {
        "BACKEND": "apps.core.storage.PublicMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-origin cookies
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'  # Allow cross-origin cookies
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email - SMTP (works with Resend, Postmark, etc.)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.resend.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'resend')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
