#!/bin/sh
set -e
echo "[comments-service] Running migrations..."
python manage.py migrate --noinput
echo "[comments-service] Starting Gunicorn (gthread for SSE)..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --worker-class gthread \
    --threads 8 \
    --timeout 360
