# 🚀 Complete Setup Guide for Savannah Microservice

## Prerequisites Installation

### 1. Install Python 3.11+

#### Option A: From Microsoft Store (Recommended for Windows)
1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Click "Get" to install

#### Option B: From Python.org
1. Go to https://www.python.org/downloads/
2. Download Python 3.11+ for Windows
3. Run the installer
4. **IMPORTANT**: Check "Add Python to PATH" during installation

#### Option C: Using Chocolatey (if you have it)
```powershell
choco install python
```

#### Option D: Using winget
```powershell
winget install Python.Python.3.11
```

### 2. Install Git (if not already installed)
1. Go to https://git-scm.com/download/win
2. Download and install Git for Windows

### 3. Install Docker Desktop
1. Go to https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Install and start Docker Desktop

## Quick Verification

After installing Python, restart your PowerShell and run:

```powershell
python --version
# Should show: Python 3.11.x or 3.12.x

pip --version
# Should show pip version

git --version
# Should show git version

docker --version
# Should show docker version
```

## Setup Commands

Once Python is installed, run these commands in order:

### 1. Create Virtual Environment
```powershell
python -m venv venv
```

### 2. Activate Virtual Environment
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat
```

### 3. Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Run Complete Setup
```powershell
python setup_complete.py
```

## Manual Setup (if automated setup fails)

### 1. Start Database
```powershell
docker-compose up -d db redis
```

### 2. Wait and Run Migrations
```powershell
# Wait 10-15 seconds for database to start
python manage.py migrate
```

### 3. Create Superuser
```powershell
python manage.py createsuperuser
```

### 4. Start Development Server
```powershell
python manage.py runserver
```

### 5. Start Celery (in new terminal)
```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1
# Then start celery
celery -A savannah_microservice worker --loglevel=info
```

## Common Issues and Solutions

### PowerShell Execution Policy
If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python not found after installation
1. Restart PowerShell/Command Prompt
2. Check if Python is in PATH: `$env:PATH`
3. Add Python to PATH manually if needed

### Docker issues
1. Make sure Docker Desktop is running
2. Check Docker status: `docker ps`
3. Restart Docker Desktop if needed

### Virtual Environment activation issues
```powershell
# If .\venv\Scripts\Activate.ps1 doesn't work, try:
.\venv\Scripts\activate.bat

# Or use full path:
C:\Users\SKULL\Documents\GitHub\Savannah-Microservice\venv\Scripts\Activate.ps1
```

## Project Structure After Setup

```
Savannah-Microservice/
├── venv/                     # Virtual environment
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── docker-compose.yml       # Docker services
├── .env                     # Environment variables
├── oauth_credentials.txt    # OAuth2 credentials (generated)
├── savannah_microservice/   # Main Django project
├── customers/              # Customer app
├── orders/                # Orders app
├── authentication/       # Auth app
├── notifications/        # SMS notifications
└── tests/                # Test files
```

## Testing the Setup

### 1. Check API Health
```powershell
curl http://localhost:8000/api/auth/health/
```

### 2. Check OAuth Credentials
Look in `oauth_credentials.txt` for:
- Client ID
- Client Secret

### 3. Test API Endpoints
Use Postman, curl, or browser to test:
- http://localhost:8000/api/customers/
- http://localhost:8000/api/orders/
- http://localhost:8000/admin/

## Next Steps After Setup

1. ✅ Review the API documentation in README.md
2. ✅ Test authentication endpoints
3. ✅ Create test customers and orders
4. ✅ Test SMS functionality (requires Africa's Talking API key)
5. ✅ Explore the admin interface
6. ✅ Run the test suite: `python manage.py test`

## Support

If you encounter issues:
1. Check the error message carefully
2. Ensure all prerequisites are installed
3. Restart services if needed
4. Check the project README.md for detailed documentation
