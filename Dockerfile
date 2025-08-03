# Use official Python image
FROM python:3.11-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ALLOWED_HOSTS=localhost,127.0.0.1 \
    CORS_ALLOWED_ORIGINS=http://localhost:3000 \
    DATABASE_URL=postgres://postgres:postgres@db:5432/project_dashboard_db

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/


# Collect static files
RUN python manage.py collectstatic --noinput

# Run database migrations
RUN python manage.py migrate --noinput

# Expose port
EXPOSE 8000

# Start Gunicorn server with WhiteNoise static file serving
CMD gunicorn project_dashboard.wsgi:application --bind 0.0.0.0:8000 --workers 3
