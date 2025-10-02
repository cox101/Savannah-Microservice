# PowerShell Setup Script for Savannah Microservice
# Run this script as Administrator for best results

param(
    [switch]$InstallPython,
    [switch]$InstallDocker,
    [switch]$SkipPrerequisites
)

Write-Host "🚀 Savannah Microservice Setup Script" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Python {
    Write-Host "📦 Installing Python..." -ForegroundColor Yellow
    
    # Try winget first
    try {
        winget install Python.Python.3.11 --silent
        Write-Host "✅ Python installed via winget" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "⚠️ Winget failed, trying chocolatey..." -ForegroundColor Yellow
    }
    
    # Try chocolatey
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install python --yes
            Write-Host "✅ Python installed via chocolatey" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "⚠️ Chocolatey not available" -ForegroundColor Yellow
    }
    
    # Manual download
    Write-Host "Please install Python manually:" -ForegroundColor Red
    Write-Host "1. Go to https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "2. Download Python 3.11+ for Windows" -ForegroundColor White
    Write-Host "3. Run installer and CHECK 'Add Python to PATH'" -ForegroundColor White
    Write-Host "4. Restart PowerShell and run this script again" -ForegroundColor White
    return $false
}

function Install-Docker {
    Write-Host "🐳 Installing Docker Desktop..." -ForegroundColor Yellow
    
    try {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install Docker.DockerDesktop --silent
            Write-Host "✅ Docker Desktop installed" -ForegroundColor Green
            Write-Host "⚠️ Please start Docker Desktop manually" -ForegroundColor Yellow
            return $true
        }
    }
    catch {
        Write-Host "Please install Docker Desktop manually:" -ForegroundColor Red
        Write-Host "1. Go to https://www.docker.com/products/docker-desktop/" -ForegroundColor White
        Write-Host "2. Download Docker Desktop for Windows" -ForegroundColor White
        Write-Host "3. Install and start Docker Desktop" -ForegroundColor White
        return $false
    }
}

function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    
    $pythonOk = $false
    $dockerOk = $false
    $gitOk = $false
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python 3\.1[1-9]|Python 3\.[2-9]") {
            Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
            $pythonOk = $true
        }
        else {
            Write-Host "❌ Python version too old or not found: $pythonVersion" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
    }
    
    # Check Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
            $dockerOk = $true
        }
    }
    catch {
        Write-Host "❌ Docker not found" -ForegroundColor Red
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>$null
        if ($gitVersion) {
            Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
            $gitOk = $true
        }
    }
    catch {
        Write-Host "❌ Git not found" -ForegroundColor Red
    }
    
    return @{
        Python = $pythonOk
        Docker = $dockerOk
        Git = $gitOk
        AllOk = $pythonOk -and $dockerOk -and $gitOk
    }
}

function Setup-VirtualEnvironment {
    Write-Host "🐍 Setting up Python virtual environment..." -ForegroundColor Yellow
    
    # Remove existing venv if it exists
    if (Test-Path "venv") {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "venv"
    }
    
    # Create virtual environment
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        return $false
    }
    
    # Activate virtual environment
    & .\venv\Scripts\Activate.ps1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment activated" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
        return $false
    }
    
    # Upgrade pip
    python -m pip install --upgrade pip
    Write-Host "✅ Pip upgraded" -ForegroundColor Green
    
    return $true
}

function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "❌ requirements.txt not found" -ForegroundColor Red
        return $false
    }
}

function Setup-Database {
    Write-Host "🐘 Setting up database..." -ForegroundColor Yellow
    
    # Start Docker containers
    docker-compose up -d db redis
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database containers started" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Failed to start database containers" -ForegroundColor Red
        Write-Host "Make sure Docker Desktop is running" -ForegroundColor Yellow
        return $false
    }
    
    # Wait for database
    Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    return $true
}

function Setup-Django {
    Write-Host "🎯 Setting up Django application..." -ForegroundColor Yellow
    
    # Run migrations
    python manage.py migrate
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to run migrations" -ForegroundColor Red
        return $false
    }
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    Write-Host "✅ Django setup complete" -ForegroundColor Green
    return $true
}

# Main execution
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Please run this script from the project root directory (where manage.py is located)" -ForegroundColor Red
    exit 1
}

# Check if running as administrator
if (-not (Test-Administrator)) {
    Write-Host "⚠️ Running without administrator privileges. Some installations might fail." -ForegroundColor Yellow
    Write-Host "Consider running PowerShell as Administrator for best results." -ForegroundColor Yellow
    Write-Host ""
}

# Install prerequisites if requested
if ($InstallPython) {
    Install-Python
    Write-Host "Please restart PowerShell and run the script again" -ForegroundColor Yellow
    exit 0
}

if ($InstallDocker) {
    Install-Docker
    Write-Host "Please start Docker Desktop and run the script again" -ForegroundColor Yellow
    exit 0
}

# Check prerequisites
if (-not $SkipPrerequisites) {
    $prereqs = Test-Prerequisites
    
    if (-not $prereqs.AllOk) {
        Write-Host "`n❌ Prerequisites not met. Please install missing components:" -ForegroundColor Red
        
        if (-not $prereqs.Python) {
            Write-Host "• Run: .\setup.ps1 -InstallPython" -ForegroundColor White
        }
        if (-not $prereqs.Docker) {
            Write-Host "• Run: .\setup.ps1 -InstallDocker" -ForegroundColor White
        }
        if (-not $prereqs.Git) {
            Write-Host "• Install Git from: https://git-scm.com/download/win" -ForegroundColor White
        }
        
        Write-Host "`nOr install manually using the SETUP_GUIDE.md" -ForegroundColor White
        exit 1
    }
}

# Setup process
Write-Host "`n🚀 Starting setup process..." -ForegroundColor Green

# Set execution policy for current user
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}
catch {
    Write-Host "⚠️ Could not set execution policy" -ForegroundColor Yellow
}

# Setup virtual environment
if (-not (Setup-VirtualEnvironment)) {
    exit 1
}

# Install dependencies
if (-not (Install-Dependencies)) {
    exit 1
}

# Setup database
if (-not (Setup-Database)) {
    exit 1
}

# Setup Django
if (-not (Setup-Django)) {
    exit 1
}

# Run complete setup if available
if (Test-Path "setup_complete.py") {
    Write-Host "🎯 Running complete setup..." -ForegroundColor Yellow
    python setup_complete.py
}

Write-Host "`n🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "2. Start development server: python manage.py runserver" -ForegroundColor White
Write-Host "3. In another terminal, start Celery: celery -A savannah_microservice worker --loglevel=info" -ForegroundColor White
Write-Host "`n🌐 Access points:" -ForegroundColor Yellow
Write-Host "• API: http://localhost:8000/api/" -ForegroundColor White
Write-Host "• Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host "• Check oauth_credentials.txt for OAuth2 credentials" -ForegroundColor White
