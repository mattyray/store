#!/bin/bash
set -e

echo "=== Starting Django server ==="
echo "PORT: $PORT"
echo "REDIS_URL: ${REDIS_URL:0:20}..."

# Set Sentry release to current git commit (Railway provides RAILWAY_GIT_COMMIT_SHA)
export SENTRY_RELEASE="${RAILWAY_GIT_COMMIT_SHA:-$(git rev-parse HEAD 2>/dev/null || echo 'unknown')}"
echo "SENTRY_RELEASE: $SENTRY_RELEASE"

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Running Django checks ==="
python manage.py check

echo "=== Generating embeddings (if needed) ==="
python manage.py generate_photo_embeddings

echo "=== Checking embeddings ==="
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production'); import django; django.setup(); from apps.catalog.models import Photo; print(f'Photos with embeddings: {Photo.objects.filter(embedding__isnull=False).count()}/{Photo.objects.count()}')"

echo "=== Cleaning up old mockup images ==="
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production'); import django; django.setup(); from apps.mockup.tasks import cleanup_old_wall_analyses; count = cleanup_old_wall_analyses(hours=24); print(f'Deleted {count} old wall analyses')"

echo "=== Starting gunicorn ==="
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --timeout 120
