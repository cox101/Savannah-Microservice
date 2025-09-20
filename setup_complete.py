import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle output."""
    print(f"🔄 {description}...")
    try:
        if sys.platform == "win32":
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True, result.stdout
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False, str(e)

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    success, output = run_command("python --version", "Checking Python", False)
    if not success:
        print("❌ Python is not installed or not in PATH")
        return False
    
    # Check Docker
    success, output = run_command("docker --version", "Checking Docker", False)
    if not success:
        print("❌ Docker is not installed or not running")
        return False
    
    # Check Docker Compose
    success, output = run_command("docker-compose --version", "Checking Docker Compose", False)
    if not success:
        print("❌ Docker Compose is not installed")
        return False
    
    print("✅ All prerequisites are satisfied")
    return True

def setup_environment():
    """Set up the development environment."""
    print("\n📦 Setting up environment...")
    
    # Install Python dependencies
    success, _ = run_command("pip install -r requirements.txt", "Installing Python dependencies")
    if not success:
        return False
    
    return True

def setup_database():
    """Set up database containers."""
    print("\n🐘 Setting up database...")
    
    # Start database containers
    success, _ = run_command("docker-compose up -d db redis", "Starting database containers")
    if not success:
        return False
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(15)
    
    # Check if containers are running
    success, output = run_command("docker-compose ps", "Checking container status", False)
    if "db" not in output or "redis" not in output:
        print("❌ Database containers are not running properly")
        return False
    
    print("✅ Database containers are ready")
    return True

def setup_django():
    """Set up Django application."""
    print("\n🎯 Setting up Django application...")
    
    # Make migrations
    success, _ = run_command("python manage.py makemigrations", "Creating migrations")
    if not success:
        return False
    
    # Apply migrations
    success, _ = run_command("python manage.py migrate", "Applying migrations")
    if not success:
        return False
    
    # Collect static files
    success, _ = run_command("python manage.py collectstatic --noinput", "Collecting static files")
    # Don't fail if this doesn't work, it's not critical for development
    
    return True

def create_test_data():
    """Create test data for development."""
    print("\n📊 Creating test data...")
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'savannah_microservice.settings')
        import django
        django.setup()
        
        from oauth2_provider.models import Application
        from django.contrib.auth.models import User
        from customers.models import Customer
        from orders.models import Order
        from decimal import Decimal
        
        # Create OAuth2 application
        if not Application.objects.filter(name="Development App").exists():
            app = Application.objects.create(
                name="Development App",
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            )
            print(f"✅ Created OAuth2 application")
            print(f"   Client ID: {app.client_id}")
            print(f"   Client Secret: {app.client_secret}")
            
            # Save credentials to a file for easy access
            with open("oauth_credentials.txt", "w") as f:
                f.write(f"Client ID: {app.client_id}\n")
                f.write(f"Client Secret: {app.client_secret}\n")
        
        # Create test customers
        if not Customer.objects.exists():
            customers_data = [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "+254700123456"
                },
                {
                    "name": "Jane Smith", 
                    "email": "jane.smith@example.com",
                    "phone_number": "+254700123457"
                },
                {
                    "name": "Bob Johnson",
                    "email": "bob.johnson@example.com", 
                    "phone_number": "+254700123458"
                }
            ]
            
            for customer_data in customers_data:
                Customer.objects.create(**customer_data)
            
            print(f"✅ Created {len(customers_data)} test customers")
        
        # Create test orders
        if not Order.objects.exists() and Customer.objects.exists():
            customers = Customer.objects.all()[:2]  # Get first 2 customers
            orders_data = [
                {
                    "customer": customers[0],
                    "item": "Laptop Computer",
                    "amount": Decimal("999.99"),
                    "quantity": 1
                },
                {
                    "customer": customers[0],
                    "item": "Wireless Mouse",
                    "amount": Decimal("29.99"),
                    "quantity": 2
                },
                {
                    "customer": customers[1],
                    "item": "Office Chair",
                    "amount": Decimal("199.99"),
                    "quantity": 1
                }
            ]
            
            for order_data in orders_data:
                Order.objects.create(**order_data)
            
            print(f"✅ Created {len(orders_data)} test orders")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Savannah Microservice Complete Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory (where manage.py is located)")
        sys.exit(1)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing tools and try again.")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed.")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("\n❌ Database setup failed.")
        sys.exit(1)
    
    # Setup Django
    if not setup_django():
        print("\n❌ Django setup failed.")
        sys.exit(1)
    
    # Create test data
    create_test_data()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Summary:")
    print("- ✅ Database (PostgreSQL) is running on port 5432")
    print("- ✅ Redis is running on port 6379") 
    print("- ✅ Django migrations have been applied")
    print("- ✅ Test data has been created")
    print("- ✅ OAuth2 credentials saved to oauth_credentials.txt")
    
    print("\n🚀 Next Steps:")
    print("1. Create a superuser (optional):")
    print("   python manage.py createsuperuser")
    print("\n2. Start the development server:")
    print("   python manage.py runserver")
    print("\n3. Start Celery worker (in another terminal):")
    print("   celery -A savannah_microservice worker --loglevel=info")
    
    print("\n🌐 Access Points:")
    print("- API Base URL: http://localhost:8000/api/")
    print("- Admin Interface: http://localhost:8000/admin/")
    print("- API Documentation: Check README.md for endpoint details")
    
    print("\n💡 Development Tips:")
    print("- Check oauth_credentials.txt for OAuth2 client credentials")
    print("- Use Postman or curl to test the API endpoints")
    print("- Monitor Celery tasks in the worker terminal")

if __name__ == "__main__":
    main()
