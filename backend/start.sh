#!/bin/bash
set -e

echo "=== Starting Django server ==="
echo "PORT: $PORT"
echo "REDIS_URL: ${REDIS_URL:0:20}..."

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Running Django checks ==="
python manage.py check

echo "=== Generating AI photo descriptions ==="
python manage.py generate_photo_descriptions

echo "=== Generating photo embeddings ==="
python manage.py generate_photo_embeddings

echo "=== Starting gunicorn ==="
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --timeout 120
