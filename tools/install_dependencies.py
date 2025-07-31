#!/usr/bin/env python3
"""
Installation and Setup Script for Shipping GUI Project
This script will install all dependencies and set up the project for development or production.
"""

import subprocess
import sys
import os
import platform


def run_command(command, description="Running command"):
    """Run a command and handle errors gracefully"""
    print(f"\n{description}...")
    print(f"Command: {command}")

    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ {description} successful")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"✗ {description} failed with exception: {e}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(
            f"✓ Python {
                version.major}.{
                version.minor}.{
                version.micro} is compatible"
        )
        return True
    else:
        print(
            f"✗ Python {
                version.major}.{
                version.minor}.{
                version.micro} is not supported. Please use Python 3.8+"
        )
        return False


def install_dependencies():
    """Install required dependencies"""
    print("\n" + "=" * 50)
    print("INSTALLING DEPENDENCIES")
    print("=" * 50)

    # Upgrade pip first
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"
    ):
        print("Warning: pip upgrade failed, continuing anyway...")

    # Install main dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements",
    ):
        print("Trying to install dependencies individually...")

        # Core dependencies
        core_deps = [
            "Flask==2.3.3",
            "Flask-SQLAlchemy==3.0.5",
            "requests==2.31.0",
            "python-dotenv==1.0.0",
            "nest_asyncio>=1.6.0",
        ]

        for dep in core_deps:
            run_command(f"{sys.executable} -m pip install {dep}", f"Installing {dep}")

    return True


def setup_environment():
    """Set up environment and configuration"""
    print("\n" + "=" * 50)
    print("SETTING UP ENVIRONMENT")
    print("=" * 50)

    # Check if .env exists
    if not os.path.exists(".env"):
        print("Creating .env file from template...")
        env_content = """# Environment Variables for Shipping GUI Project
# Flask Configuration
FLASK_SECRET_KEY=unified_order_system_2025_production_secret_key_v2

# Veeqo API Configuration (Replace with your actual key)
VEEQO_API_KEY=your_veeqo_api_key_here

# Easyship API Configuration (Replace with your actual key)
EASYSHIP_API_KEY=your_easyship_api_key_here

# Application Settings
DEBUG=True
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///shipping_automation.db

# Server Configuration
HOST=127.0.0.1
PORT=5000

# HuggingFace Token (Optional)
HF_TOKEN=your_huggingface_token_here
"""
        try:
            with open(".env", "w") as f:
                f.write(env_content)
            print("✓ Created .env file (please update with your actual API keys)")
        except Exception as e:
            print(f"✗ Failed to create .env file: {e}")
    else:
        print("✓ .env file already exists")

    return True


def test_imports():
    """Test critical imports"""
    print("\n" + "=" * 50)
    print("TESTING IMPORTS")
    print("=" * 50)

    test_imports_list = [
        ("flask", "Flask"),
        ("requests", "HTTP requests"),
        ("dotenv", "Environment variables"),
        ("app", "Main application"),
    ]

    all_passed = True
    for module, description in test_imports_list:
        try:
            __import__(module)
            print(f"✓ {description} import successful")
        except ImportError as e:
            print(f"✗ {description} import failed: {e}")
            all_passed = False

    return all_passed


def create_database():
    """Initialize database"""
    print("\n" + "=" * 50)
    print("INITIALIZING DATABASE")
    print("=" * 50)

    try:
        from app import app
        from models import db

        with app.app_context():
            db.create_all()
            print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


def main():
    """Main installation process"""
    print("=" * 60)
    print("SHIPPING GUI PROJECT - INSTALLATION & SETUP")
    print("=" * 60)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("✗ Dependency installation failed")
        sys.exit(1)

    # Setup environment
    if not setup_environment():
        print("✗ Environment setup failed")
        sys.exit(1)

    # Test imports
    if not test_imports():
        print("✗ Import tests failed")
        print(
            "Some dependencies may be missing. Try running: pip install -r requirements.txt"
        )

    # Initialize database
    if not create_database():
        print("✗ Database initialization failed")
        print("You may need to run this manually later")

    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE!")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("1. Update .env file with your actual API keys")
    print("2. Run the application: python app.py")
    print("3. Open browser to: http://127.0.0.1:5000")
    print("\nFor development:")
    print("- Run tests: python -m pytest tests/")
    print("- Check setup: python validate_setup.py")
    print("\nFor production:")
    print("- Use gunicorn: gunicorn -c gunicorn_config.py app:app")


if __name__ == "__main__":
    main()
