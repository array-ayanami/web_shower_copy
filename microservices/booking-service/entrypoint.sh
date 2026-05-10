#!/bin/sh
set -e
echo "[booking-service] Running migrations..."
python manage.py migrate --noinput
echo "[booking-service] Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 60
