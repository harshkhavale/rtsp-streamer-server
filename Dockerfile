# Use an official slim Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (without redis-server)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libopencv-dev \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Collect static files (important for production)
RUN python manage.py collectstatic --noinput

# Expose port (used by Daphne or ASGI server)
EXPOSE 8000

# Run the app using Daphne for WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "rtsp_backend.asgi:application"]
