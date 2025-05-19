# Use an official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /code

# Copy dependencies
COPY requirements.txt /code/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --default-timeout=60 --retries=10 --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

# Expose port
EXPOSE 8000

# Start the development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
