#!/bin/sh
set -e
echo "[auth-service] Running migrations..."
python manage.py migrate --noinput
echo "[auth-service] Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 60
