#!/bin/bash
# Build script for Unified Order & Warehouse Management System

set -e  # Exit on any error

echo "🚀 Building Unified Order & Warehouse Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
print_status "Checking Python installation..."
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        print_error "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    else
        PYTHON_CMD=python3
    fi
else
    PYTHON_CMD=python
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
print_success "Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed successfully"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Run basic validation
print_status "Running basic validation..."
$PYTHON_CMD -c "import app; print('✓ App module imports successfully')"

# Check for essential files
essential_files=("app.py" "wsgi.py" "templates/index.html")
for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file found"
    else
        print_error "✗ $file missing"
        exit 1
    fi
done

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data static/css static/js static/images
print_success "Directories created"

# Build summary
print_status "Build Summary:"
echo "  ✓ Virtual environment: venv/"
echo "  ✓ Dependencies installed from requirements.txt"
echo "  ✓ Essential files validated"
echo "  ✓ Directory structure created"
echo ""
print_success "🎉 Build completed successfully!"
echo ""
print_status "Next steps:"
echo "  1. Configure environment variables in .env file"
echo "  2. Start the application: python wsgi.py"
echo "  3. Or use Docker: docker build -t shipping-gui ."
echo "  4. Access at: http://localhost:5000"
echo ""
