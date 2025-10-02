#!/usr/bin/env python
"""
Django Database Setup Script for Savannah Microservice
"""
import os
import sys
import django
import subprocess
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'savannah_microservice.settings')

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_database_connection():
    """Check if database connection is working."""
    try:
        django.setup()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_initial_data():
    """Create initial data for the application."""
    try:
        django.setup()
        from oauth2_provider.models import Application
        from django.contrib.auth.models import User
        
        # Create OAuth2 application for testing
        if not Application.objects.filter(name="Test Application").exists():
            app = Application.objects.create(
                name="Test Application",
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            )
            print(f"✅ Created OAuth2 test application")
            print(f"   Client ID: {app.client_id}")
            print(f"   Client Secret: {app.client_secret}")
        else:
            print("ℹ️  OAuth2 test application already exists")
            
        print("✅ Initial data creation completed")
        return True
    except Exception as e:
        print(f"❌ Initial data creation failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Django Database for Savannah Microservice")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not (BASE_DIR / 'manage.py').exists():
        print("❌ manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Please ensure PostgreSQL is running and accessible.")
        print("   You can start it with: docker-compose up -d db")
        sys.exit(1)
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Applying migrations"):
        sys.exit(1)
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠️  Static files collection failed, but continuing...")
    
    # Create initial data
    create_initial_data()
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Start the development server: python manage.py runserver")
    print("3. Start Celery worker: celery -A savannah_microservice worker --loglevel=info")
    print("\nAPI will be available at: http://localhost:8000/api/")
    print("Admin interface: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()
