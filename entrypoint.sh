#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Running makemigrations..."
python manage.py makemigrations --noinput

echo "📦 Applying migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating default superuser..."
# Optional: auto-create superuser if it doesn't exist
echo "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
" | python manage.py shell

echo "✅ Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8000 rtsp_backend.asgi:application
