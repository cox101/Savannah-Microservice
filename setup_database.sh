#!/bin/bash
# Database Setup Script for Savannah Microservice

echo "🚀 Setting up Savannah Microservice Database..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Start PostgreSQL and Redis containers
echo "🐘 Starting PostgreSQL and Redis containers..."
docker-compose up -d db redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if containers are running
if docker-compose ps | grep -q "db.*Up"; then
    echo "✅ PostgreSQL container is running"
else
    echo "❌ PostgreSQL container failed to start"
    docker-compose logs db
    exit 1
fi

if docker-compose ps | grep -q "redis.*Up"; then
    echo "✅ Redis container is running"
else
    echo "❌ Redis container failed to start"
    docker-compose logs redis
    exit 1
fi

echo "🎉 Database containers are ready!"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Run migrations: python manage.py migrate"
echo "3. Create superuser: python manage.py createsuperuser"
echo "4. Start the application: python manage.py runserver"
echo ""
echo "Database connection details:"
echo "- Host: localhost"
echo "- Port: 5432"
echo "- Database: savannah_microservice"
echo "- Username: postgres"
echo "- Password: postgres"
