@echo off
REM Docker management script for Project Dashboard (Windows)

if "%1"=="start" (
    echo Starting the application...
    docker compose up -d
    goto :eof
)

if "%1"=="stop" (
    echo Stopping the application...
    docker compose down
    goto :eof
)

if "%1"=="restart" (
    echo Restarting the application...
    docker compose down
    docker compose up -d
    goto :eof
)

if "%1"=="logs" (
    echo Showing logs...
    docker compose logs -f
    goto :eof
)

if "%1"=="build" (
    echo Building the application...
    docker compose build --no-cache
    goto :eof
)

if "%1"=="shell" (
    echo Opening shell in the container...
    docker compose exec web bash
    goto :eof
)

if "%1"=="migrate" (
    echo Running migrations...
    docker compose exec web python manage.py migrate
    goto :eof
)

if "%1"=="collectstatic" (
    echo Collecting static files...
    docker compose exec web python manage.py collectstatic --noinput
    goto :eof
)

if "%1"=="test" (
    echo Running tests...
    docker compose exec web python manage.py test
    goto :eof
)

echo Usage: %0 {start^|stop^|restart^|logs^|build^|shell^|migrate^|collectstatic^|test}
echo.
echo Commands:
echo   start        - Start the application in detached mode
echo   stop         - Stop the application
echo   restart      - Restart the application
echo   logs         - Show application logs
echo   build        - Rebuild the Docker image
echo   shell        - Open shell in the container
echo   migrate      - Run database migrations
echo   collectstatic - Collect static files
echo   test         - Run tests 