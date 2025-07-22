# PowerShell Build Script for Unified Order & Warehouse Management System
# Run this script in PowerShell: .\build.ps1

param(
    [switch]$Clean,
    [switch]$Docker,
    [string]$Environment = "production"
)

# Colors for output
$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Status {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

Write-ColorOutput "🚀 Building Unified Order & Warehouse Management System..." "Magenta"

# Clean build option
if ($Clean) {
    Write-Status "Cleaning previous build..."
    if (Test-Path "venv") {
        Remove-Item -Recurse -Force "venv"
        Write-Success "Cleaned virtual environment"
    }
    if (Test-Path "logs") {
        Remove-Item -Recurse -Force "logs"
        Write-Success "Cleaned logs directory"
    }
}

# Check if Python is installed
Write-Status "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        Write-Success "Python $($matches[1]) detected"
        $pythonCmd = "python"
    }
} catch {
    try {
        $pythonVersion = python3 --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            Write-Success "Python $($matches[1]) detected"
            $pythonCmd = "python3"
        }
    } catch {
        Write-Error-Custom "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Status "Creating virtual environment..."
    & $pythonCmd -m venv venv
    Write-Success "Virtual environment created"
} else {
    Write-Status "Virtual environment already exists"
}

# Activate virtual environment
Write-Status "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
Write-Status "Installing dependencies..."
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Success "Dependencies installed successfully"
} else {
    Write-Error-Custom "requirements.txt not found"
    exit 1
}

# Run basic validation
Write-Status "Running basic validation..."
try {
    & $pythonCmd -c "import app; print('✓ App module imports successfully')"
    Write-Success "App validation passed"
} catch {
    Write-Error-Custom "App validation failed"
    exit 1
}

# Check for essential files
$essentialFiles = @("app.py", "wsgi.py", "templates\index.html")
foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Success "✓ $file found"
    } else {
        Write-Error-Custom "✗ $file missing"
        exit 1
    }
}

# Create necessary directories
Write-Status "Creating necessary directories..."
$directories = @("logs", "data", "static\css", "static\js", "static\images")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Success "Directories created"

# Docker build option
if ($Docker) {
    Write-Status "Building Docker image..."
    try {
        docker build -t shipping-gui .
        Write-Success "Docker image built successfully"
        Write-Status "To run with Docker: docker run -p 5000:5000 shipping-gui"
    } catch {
        Write-Warning "Docker build failed. Make sure Docker is installed and running."
    }
}

# Create .env template if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Status "Creating .env template..."
    @"
# Environment Configuration
FLASK_ENV=$Environment
FLASK_DEBUG=0
FLASK_SECRET_KEY=your-secret-key-here

# API Keys (replace with your actual keys)
VEEQO_API_KEY=your-veeqo-api-key
EASYSHIP_API_KEY=your-easyship-api-key

# Database Configuration (if needed)
DATABASE_URL=sqlite:///data/app.db

# Port Configuration
PORT=5000
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Success ".env template created"
}

# Build summary
Write-Status "Build Summary:"
Write-Host "  ✓ Virtual environment: venv\"
Write-Host "  ✓ Dependencies installed from requirements.txt"
Write-Host "  ✓ Essential files validated"
Write-Host "  ✓ Directory structure created"
Write-Host "  ✓ Environment template created"

Write-Success "🎉 Build completed successfully!"
Write-Host ""
Write-Status "Next steps:"
Write-Host "  1. Configure your API keys in the .env file"
Write-Host "  2. Start the application: python wsgi.py"
Write-Host "  3. Or activate venv and run: python app.py"
if ($Docker) {
    Write-Host "  4. Or use Docker: docker run -p 5000:5000 shipping-gui"
}
Write-Host "  5. Access at: http://localhost:5000"
Write-Host ""
Write-ColorOutput "Application is ready for deployment! 🚀" "Green"
