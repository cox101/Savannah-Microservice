@echo off
REM Database Setup Script for Savannah Microservice (Windows)

echo 🚀 Setting up Savannah Microservice Database...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Start PostgreSQL and Redis containers
echo 🐘 Starting PostgreSQL and Redis containers...
docker-compose up -d db redis

REM Wait for PostgreSQL to be ready
echo ⏳ Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

REM Check if containers are running
docker-compose ps | findstr "db" | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL container is running
) else (
    echo ❌ PostgreSQL container failed to start
    docker-compose logs db
    pause
    exit /b 1
)

docker-compose ps | findstr "redis" | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ Redis container is running
) else (
    echo ❌ Redis container failed to start
    docker-compose logs redis
    pause
    exit /b 1
)

echo 🎉 Database containers are ready!
echo.
echo Next steps:
echo 1. Install Python dependencies: pip install -r requirements.txt
echo 2. Run migrations: python manage.py migrate
echo 3. Create superuser: python manage.py createsuperuser
echo 4. Start the application: python manage.py runserver
echo.
echo Database connection details:
echo - Host: localhost
echo - Port: 5432
echo - Database: savannah_microservice
echo - Username: postgres
echo - Password: postgres

pause
