"""
WSGI config for Photography Store.
"""
import os
import sys

print("=== WSGI: Starting import ===", flush=True)
sys.stdout.flush()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

print("=== WSGI: About to call get_wsgi_application ===", flush=True)
sys.stdout.flush()

from django.core.wsgi import get_wsgi_application

print("=== WSGI: Calling get_wsgi_application ===", flush=True)
sys.stdout.flush()

application = get_wsgi_application()

print("=== WSGI: Application created successfully ===", flush=True)
sys.stdout.flush()
