#!/usr/bin/env python3
"""
Simple startup script for Shipping GUI application
Run this to start the application immediately
"""

import os
import sys
import subprocess


def main():
    print("=" * 60)
    print("SHIPPING GUI APPLICATION - QUICK START")
    print("=" * 60)

    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found!")
        print("Please run this script from the project root directory.")
        return False

    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
        from dotenv import load_dotenv

        load_dotenv()

    # Check for API keys
    veeqo_key = os.getenv("VEEQO_API_KEY")
    easyship_key = os.getenv("EASYSHIP_API_KEY")

    if not veeqo_key or veeqo_key.startswith("your_"):
        print("⚠️  Warning: VEEQO_API_KEY not set in .env file")

    if not easyship_key or easyship_key.startswith("your_"):
        print("⚠️  Warning: EASYSHIP_API_KEY not set in .env file")

    # Try to import the app
    try:
        from app import app

        print("✅ Flask application loaded successfully")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("Run: pip install -r requirements.txt")
        return False

    # Start the application
    print("\n🚀 Starting Flask development server...")
    print("📱 Application will be available at: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop the server\n")

    try:
        app.run(host="127.0.0.1", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 For help, run: python comprehensive_validate.py")
        sys.exit(1)
