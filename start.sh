#!/bin/sh

set -e

echo "Running migrations..."
uv run python manage.py migrate

echo "Starting Django development server..."
uv run python manage.py runserver 0.0.0.0:8000



