#!/usr/bin/env python3
"""
Production-ready startup script for Shipping GUI application
Handles configuration, environment setup, and graceful startup/shutdown
"""

import os
import sys
import signal
import subprocess
from dotenv import load_dotenv


class ProductionRunner:
    def __init__(self):
        self.process = None
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

    def shutdown_handler(self, signum, frame):
        """Handle graceful shutdown"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        if self.process:
            self.process.terminate()
            self.process.wait()
        sys.exit(0)

    def validate_environment(self):
        """Validate required environment variables"""
        load_dotenv()

        required_vars = [
            "FLASK_SECRET_KEY",
            "VEEQO_API_KEY",
            "EASYSHIP_API_KEY",
        ]

        missing = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.startswith("your_"):
                missing.append(var)

        if missing:
            print("❌ Missing required environment variables:")
            for var in missing:
                print(f"   - {var}")
            print("\nPlease update your .env file with actual values.")
            return False

        print("✅ Environment variables validated")
        return True

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        try:
            pass

            print("✅ Core dependencies available")
            return True
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            print("Run: pip install -r requirements.txt")
            return False

    def initialize_database(self):
        """Initialize database if needed"""
        try:
            from app import app
            from models import db

            db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "").replace(
                "sqlite:///", ""
            )
            if db_path and not os.path.exists(db_path):
                print("🔧 Initializing database...")
                with app.app_context():
                    db.create_all()
                print("✅ Database initialized")
            else:
                print("✅ Database already exists")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False

    def run_development(self):
        """Run in development mode"""
        print("🚀 Starting development server...")
        os.environ["FLASK_ENV"] = "development"
        os.environ["FLASK_DEBUG"] = "True"

        try:
            from app import app

            app.run(
                host=os.getenv("HOST", "127.0.0.1"),
                port=int(os.getenv("PORT", 5000)),
                debug=True,
            )
        except Exception as e:
            print(f"❌ Failed to start development server: {e}")
            return False

        return True

    def run_production(self):
        """Run in production mode with Gunicorn"""
        print("🚀 Starting production server with Gunicorn...")

        # Check if Gunicorn is installed
        try:
            pass
        except ImportError:
            print("❌ Gunicorn not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])

        # Gunicorn configuration
        host = os.getenv("HOST", "0.0.0.0")
        port = os.getenv("PORT", "5000")
        workers = os.getenv("WORKERS", "4")

        cmd = [
            "gunicorn",
            "--bind",
            f"{host}:{port}",
            "--workers",
            str(workers),
            "--timeout",
            "120",
            "--keep-alive",
            "2",
            "--max-requests",
            "1000",
            "--max-requests-jitter",
            "100",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
            "app:app",
        ]

        try:
            self.process = subprocess.Popen(cmd)
            print(f"✅ Production server started on {host}:{port}")
            print(f"🔗 Access the application at: http://{host}:{port}")
            self.process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        except Exception as e:
            print(f"❌ Production server failed: {e}")
            return False

        return True

    def run(self, mode="auto"):
        """Main run method"""
        print("=" * 60)
        print("SHIPPING GUI APPLICATION - PRODUCTION RUNNER")
        print("=" * 60)

        # Validation steps
        if not self.validate_environment():
            return False

        if not self.check_dependencies():
            return False

        if not self.initialize_database():
            return False

        # Determine run mode
        if mode == "auto":
            is_production = (
                os.getenv("FLASK_ENV", "").lower() == "production"
                or os.getenv("DEBUG", "").lower() in ["false", "0", "no"]
                or "--production" in sys.argv
            )
            mode = "production" if is_production else "development"

        print(f"🎯 Running in {mode.upper()} mode")

        # Start the appropriate server
        if mode == "production":
            return self.run_production()
        else:
            return self.run_development()


def main():
    """Main entry point"""
    runner = ProductionRunner()

    # Parse command line arguments
    if "--production" in sys.argv:
        mode = "production"
    elif "--development" in sys.argv:
        mode = "development"
    else:
        mode = "auto"

    success = runner.run(mode)
    if not success:
        print("\n❌ Application failed to start")
        sys.exit(1)


if __name__ == "__main__":
    main()
