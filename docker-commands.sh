#!/bin/bash

# Docker management script for Project Dashboard

case "$1" in
    "start")
        echo "Starting the application..."
        docker compose up -d
        ;;
    "stop")
        echo "Stopping the application..."
        docker compose down
        ;;
    "restart")
        echo "Restarting the application..."
        docker compose down
        docker compose up -d
        ;;
    "logs")
        echo "Showing logs..."
        docker compose logs -f
        ;;
    "build")
        echo "Building the application..."
        docker compose build --no-cache
        ;;
    "shell")
        echo "Opening shell in the container..."
        docker compose exec web bash
        ;;
    "migrate")
        echo "Running migrations..."
        docker compose exec web python manage.py migrate
        ;;
    "collectstatic")
        echo "Collecting static files..."
        docker compose exec web python manage.py collectstatic --noinput
        ;;
    "test")
        echo "Running tests..."
        docker compose exec web python manage.py test
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|build|shell|migrate|collectstatic|test}"
        echo ""
        echo "Commands:"
        echo "  start        - Start the application in detached mode"
        echo "  stop         - Stop the application"
        echo "  restart      - Restart the application"
        echo "  logs         - Show application logs"
        echo "  build        - Rebuild the Docker image"
        echo "  shell        - Open shell in the container"
        echo "  migrate      - Run database migrations"
        echo "  collectstatic - Collect static files"
        echo "  test         - Run tests"
        exit 1
        ;;
esac 