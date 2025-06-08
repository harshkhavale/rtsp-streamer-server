#!/bin/bash

# Apply migrations
echo "🚀 Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create default superuser if not exists
echo "👤 Creating default superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
END

# Start server (Daphne or Gunicorn)
echo "✅ Starting server..."
exec daphne -b 0.0.0.0 -p 8000 rtsp_backend.asgi:application
